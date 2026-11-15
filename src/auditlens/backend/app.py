"""Run: uvicorn auditlens.backend.app:app --host 127.0.0.1 --port 8000 --workers 1."""

import logging
import os
import threading
import time
from contextlib import asynccontextmanager

# Apply before importing Polars/NumPy through the existing inference API.
os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles

from .config import Settings
from .errors import APIError
from .schemas import (
    AnalyzeResponse,
    DemoRequest,
    DemoResponse,
    ErrorResponse,
    HealthResponse,
    ModelResponse,
)
from .service import ASSETS, ROOT, HandbookService
from .uploads import multipart_inputs, read_upload

LOG = logging.getLogger("auditlens.backend")
ERRORS = {code: {"model": ErrorResponse} for code in (400, 413, 422, 429, 500, 503)}


def error_response(status, code, message):
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message}},
        headers={"Retry-After": "1"} if status == 429 else None,
    )


class SanitizedErrors:
    """Prevent ASGI servers from logging parser/model exception messages containing data."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        started = False

        async def tracked_send(message):
            nonlocal started
            if message["type"] == "http.response.start":
                started = True
            await send(message)

        try:
            await self.app(scope, receive, tracked_send)
        except Exception as exc:
            LOG.error("Unexpected backend failure (%s)", type(exc).__name__)
            if not started:
                await error_response(
                    500, "internal_error", "Request failed unexpectedly; uploaded data was discarded."
                )(scope, receive, send)


class RequestGate:
    """Bound bodies and admit expensive requests before multipart parsing, without queuing."""

    def __init__(self, app, settings, slots):
        self.app, self.settings, self.slots = app, settings, slots

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST":
            return await self.app(scope, receive, send)
        acquired = False
        try:
            if scope["path"] in {"/api/v1/analyze", "/api/v1/demo/analyze"}:
                acquired = self.slots.acquire(blocking=False)
                if not acquired:
                    return await error_response(
                        429, "analysis_busy", "Analysis capacity is busy; retry shortly."
                    )(scope, receive, send)
            body = bytearray()
            headers = dict(scope["headers"])
            declared = headers.get(b"content-length")
            if declared is not None:
                try:
                    size = int(declared)
                    if size < 0:
                        raise ValueError
                except ValueError:
                    return await error_response(400, "invalid_request", "Invalid Content-Length.")(
                        scope, receive, send
                    )
                if size > self.settings.max_request_bytes:
                    return await error_response(
                        413, "request_too_large", "Request exceeds the configured byte limit."
                    )(scope, receive, send)
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                chunk = message.get("body", b"")
                if len(body) + len(chunk) > self.settings.max_request_bytes:
                    return await error_response(
                        413, "request_too_large", "Request exceeds the configured byte limit."
                    )(scope, receive, send)
                body.extend(chunk)
                if not message.get("more_body", False):
                    break
            delivered = False

            async def replay():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {"type": "http.request", "body": bytes(body), "more_body": False}
                return await receive()

            return await self.app(scope, replay, send)
        finally:
            if acquired:
                self.slots.release()


def create_app(settings=None):
    settings = settings or Settings.from_env()
    service = HandbookService(settings)
    slots = threading.BoundedSemaphore(settings.max_concurrent)

    @asynccontextmanager
    async def lifespan(app):
        try:
            await run_in_threadpool(service.load)
        except Exception:
            service.model = None
            LOG.error("Registered Handbook model unavailable at startup")
        yield
        service.model = None

    app = FastAPI(
        title="AuditLens AI — Handbook",
        version="1.0.0",
        lifespan=lifespan,
        description="Synthetic-data research prototype. Scores are uncalibrated review priorities. "
        "This project is a prototype and is not financial advice.",
        responses=ERRORS,
    )
    app.state.service, app.state.analysis_slots, app.state.settings = service, slots, settings

    @app.exception_handler(APIError)
    async def api_error(request, exc):
        return error_response(exc.status, exc.code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return error_response(
            422, "invalid_request", "Invalid request fields or JSON; top_k must be a positive integer."
        )

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        return error_response(exc.status_code, "http_error", "Request cannot be handled at this endpoint.")

    @app.exception_handler(Exception)
    async def unexpected_error(request, exc):
        # Neither exception text nor uploaded records are logged or returned.
        LOG.error("Unexpected backend failure (%s)", type(exc).__name__)
        return error_response(
            500, "internal_error", "Analysis failed unexpectedly; uploaded data was discarded."
        )

    @app.get("/api/v1/health", response_model=HealthResponse, responses={503: {"model": HealthResponse}})
    async def health():
        payload = service.health()
        return JSONResponse(payload, status_code=200 if payload["model_available"] else 503)

    @app.get("/api/v1/model", response_model=ModelResponse)
    async def model():
        return service.describe()

    def analyze_files(files, top_k, started):
        current = read_upload(*files["transactions"], settings.max_transactions, settings)
        history = (
            read_upload(*files["history"], settings.max_history, settings) if "history" in files else None
        )
        response = service.analyze(current, history, top_k)
        response["processing_time_ms"] = round((time.perf_counter() - started) * 1000, 3)
        return AnalyzeResponse(**response)

    def require_model():
        if service.model is None:
            raise APIError(503, "model_unavailable", "Registered Handbook model could not be loaded.")

    upload_schema = {
        "requestBody": {
            "required": True,
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["transactions", "top_k"],
                        "properties": {
                            "transactions": {
                                "type": "string",
                                "format": "binary",
                                "description": "Exact Handbook CSV/XLSX schema",
                            },
                            "history": {
                                "type": "string",
                                "format": "binary",
                                "description": "Optional strictly preceding same-schema history",
                            },
                            "top_k": {"type": "integer", "minimum": 1, "maximum": 999999999999},
                        },
                    }
                }
            },
        }
    }

    @app.post("/api/v1/analyze", response_model=AnalyzeResponse, openapi_extra=upload_schema)
    async def analyze(request: Request):
        started = time.perf_counter()
        require_model()
        files, top_k = await multipart_inputs(request, settings)
        return await run_in_threadpool(analyze_files, files, top_k, started)

    def demo_files():
        return {
            name: ((ASSETS / f"{name}.csv").read_bytes(), f"{name}.csv")
            for name in ("transactions", "history")
        }

    @app.get("/api/v1/demo", response_model=DemoResponse)
    async def demo():
        files = demo_files()
        current = read_upload(*files["transactions"], settings.max_transactions, settings)
        return dict(
            id="self-authored-shop-v1",
            description="Ordinary purchases, changed spending, new terminal and cold customer. "
            "Actual ranking is model-dependent; this example is not an accuracy benchmark.",
            provenance="Deterministic self-authored fictional records; no publisher dataset rows or labels.",
            transactions=[
                {**r, "timestamp": r["timestamp"].strftime("%Y-%m-%dT%H:%M:%S")} for r in current.to_dicts()
            ],
            history_count=93,
            downloads={name: f"/api/v1/templates/{name}.csv" for name in files},
            analysis_url="/api/v1/demo/analyze",
        )

    @app.post("/api/v1/demo/analyze", response_model=AnalyzeResponse)
    async def demo_analyze(body: DemoRequest = DemoRequest()):
        started = time.perf_counter()
        require_model()
        return await run_in_threadpool(analyze_files, demo_files(), body.top_k, started)

    @app.get(
        "/api/v1/templates/{name}",
        response_class=Response,
        responses={200: {"content": {"text/csv": {"schema": {"type": "string"}}}}},
    )
    async def template(name: str):
        # A closed allowlist, never a client-provided filesystem path.
        if name not in {"transactions.csv", "history.csv"}:
            raise APIError(404, "template_not_found", "Use transactions.csv or history.csv.")
        return Response(
            (ASSETS / name).read_bytes(),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{name}"'},
        )

    # Catch unexpected errors before Starlette re-raises them to the ASGI server's logger.
    app.add_middleware(SanitizedErrors)
    app.add_middleware(RequestGate, settings=settings, slots=slots)
    if settings.frontend_origin:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[settings.frontend_origin],
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type"],
            allow_credentials=False,
        )

    # Hash-based React navigation needs only index.html and its built assets.
    # Mount last so API/docs keep their contracts; never expose the repository.
    frontend_dist = ROOT / "frontend" / "dist"
    if (frontend_dist / "index.html").is_file():
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
    return app


app = create_app()
