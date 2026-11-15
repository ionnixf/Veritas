"""Real CPU model integration and bounded, private upload handling."""

import asyncio
import io
import json
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import polars as pl
import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook

from auditlens.backend.app import create_app
from auditlens.backend.config import Settings
from auditlens.backend.service import ASSETS, BENCHMARK, ROOT, HandbookService
from auditlens.handbook import FEATURES, RAW_COLUMNS
from auditlens.inference import DISCLAIMER


@pytest.fixture(scope="module")
def app():
    return create_app()


@pytest.fixture(scope="module")
def client(app):
    with TestClient(app) as client:
        yield client


def csv_data(name="transactions"):
    return (ASSETS / f"{name}.csv").read_bytes()


def xlsx_data(data=None):
    frame = pl.read_csv(
        io.BytesIO(data or csv_data()), schema_overrides={c: pl.String for c in RAW_COLUMNS[:-1]}
    )
    book = Workbook()
    book.active.append(frame.columns)
    for row in frame.iter_rows():
        book.active.append(row)
    stream = io.BytesIO()
    book.save(stream)
    book.close()
    return stream.getvalue()


def upload(client, data=None, *, history=True, top_k="5", filename="table.csv", past=None):
    files = {"transactions": (filename, data if data is not None else csv_data())}
    if history:
        files["history"] = ("history.csv", past if past is not None else csv_data("history"))
    return client.post("/api/v1/analyze", files=files, data={"top_k": top_k})


def stable(payload):
    return {k: v for k, v in payload.items() if k != "processing_time_ms"}


def test_ready_and_frozen_benchmarks(client):
    assert client.get("/api/v1/health").json() == {
        "status": "ready",
        "model_available": True,
        "model_id": "handbook",
        "model_version": "handbook-xgboost-v1",
        "device": "cpu",
    }
    response = client.get("/api/v1/model")
    assert response.status_code == 200
    result = response.json()
    report = json.loads(BENCHMARK.read_text())
    frozen = report["candidate"]["test"]
    assert result["benchmark"]["test"]["average_precision"] == frozen["average_precision"]
    assert result["benchmark"]["test"]["precision_at_1000"] == 0.794
    assert result["baselines"]["amount"]["positives_at_1000"] == 569
    assert result["benchmark_provenance"]["test_previously_opened"]
    assert result["benchmark_provenance"]["synthetic"]
    assert result["history_requirements"]["required_for_acceptance"] is False
    assert result["disclaimer"] == DISCLAIMER


def test_benchmark_split_periods_match_selected_artifact(client):
    result = client.get("/api/v1/model").json()
    metadata = json.loads((ROOT / "models" / result["version"] / "metadata.json").read_text())
    assert result["benchmark_provenance"]["split_periods"] == {
        "train": metadata["training_period"],
        "validation": metadata["validation_period"],
        "test": metadata["test_period"],
    }


def test_model_failure_and_single_startup_load(monkeypatch):
    import auditlens.backend.service as service_module

    calls = []

    def failing(model_id, **kwargs):
        calls.append((model_id, kwargs))
        raise RuntimeError("internal-secret")

    monkeypatch.setattr(service_module, "load_registered_model", failing)
    with TestClient(create_app()) as client:
        assert client.get("/api/v1/health").status_code == 503
        assert client.get("/api/v1/health").json()["model_available"] is False
        assert client.get("/api/v1/model").json()["available"] is False
        response = upload(client)
        assert response.status_code == 503
        assert "internal-secret" not in response.text
        assert client.post("/api/v1/demo/analyze").status_code == 503
    assert calls == [("handbook", {"threads": 2, "allow_research": True})]


def test_real_cpu_inference_csv_and_response(client, app):
    result = upload(client).json()
    frame = pl.read_csv(io.BytesIO(csv_data()))
    history = pl.read_csv(io.BytesIO(csv_data("history")))
    actual = app.state.service.model.analyze(frame, history=history)
    assert result["analyzed_count"] == 5 and result["history_count"] == 93
    assert result["queue_count"] == result["top_k"] == 5
    assert [r["score"] for r in result["operations"]] == [r["risk_score"] for r in actual]
    assert [r["record_id"] for r in result["operations"]] == [r["record_id"] for r in actual]
    assert [r["rank"] for r in result["operations"]] == [1, 2, 3, 4, 5]
    assert all(r["reasons"] == source["reasons"] for r, source in zip(result["operations"], actual))
    assert all(set(RAW_COLUMNS).issubset(r) for r in result["operations"])
    assert result["processing_time_ms"] > 0 and result["research_status"] == "RESEARCH DEMO"
    assert any("cold start" in w for w in result["warnings"])
    assert app.state.service.model.pipeline.get_params()["device"] == "cpu"


def test_xlsx_and_csv_equivalent(client):
    csv_result = upload(client)
    xlsx_result = upload(client, xlsx_data(), filename="table.xlsx")
    assert xlsx_result.status_code == 200, xlsx_result.text
    assert stable(csv_result.json()) == stable(xlsx_result.json())
    response = client.post(
        "/api/v1/analyze",
        files={
            "transactions": ("table.xlsx", xlsx_data()),
            "history": ("history.xlsx", xlsx_data(csv_data("history"))),
        },
        data={"top_k": "5"},
    )
    assert response.status_code == 200
    assert stable(csv_result.json()) == stable(response.json())


@pytest.mark.parametrize("column,value", [("A2", 1), ("C2", 1), ("D2", 1), ("E2", True)])
def test_xlsx_rejects_lossy_ids_and_booleans(client, column, value):
    from openpyxl import load_workbook

    book = load_workbook(io.BytesIO(xlsx_data()))
    book.active[column] = value
    stream = io.BytesIO()
    book.save(stream)
    book.close()
    assert upload(client, stream.getvalue(), filename="bad.xlsx").status_code == 422


def test_xlsx_ignores_untrusted_dimensions(client):
    stream = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(xlsx_data())) as source, zipfile.ZipFile(stream, "w") as output:
        for entry in source.infolist():
            contents = source.read(entry)
            if entry.filename == "xl/worksheets/sheet1.xml":
                contents = contents.replace(b'ref="A1:E6"', b'ref="A1:E2"')
            output.writestr(entry, contents)
    response = upload(client, stream.getvalue(), filename="dimensions.xlsx")
    assert response.status_code == 200
    assert response.json()["analyzed_count"] == 5


def test_xlsx_datetime_cells_without_dimensions(client):
    from datetime import datetime

    frame = pl.read_csv(io.BytesIO(csv_data()))
    book = Workbook(write_only=True)
    sheet = book.create_sheet()
    sheet.append(frame.columns)
    for row in frame.iter_rows():
        sheet.append([row[0], datetime.fromisoformat(row[1]), *row[2:]])
    stream = io.BytesIO()
    book.save(stream)
    book.close()
    response = upload(client, stream.getvalue(), filename="datetime.xlsx")
    assert response.status_code == 200
    assert stable(response.json()) == stable(upload(client).json())


@pytest.mark.parametrize("value", ["0", "-1", "1.5", "true", "", "NaN", "1000000000000"])
def test_invalid_top_k(client, value):
    assert upload(client, top_k=value).status_code == 422


@pytest.mark.parametrize("top_k,expected", [(1, 1), (3, 3), (100, 5)])
def test_budget_and_count(client, top_k, expected):
    result = upload(client, top_k=str(top_k)).json()
    assert result["top_k"] == top_k and result["queue_count"] == expected
    assert len(result["operations"]) == expected


def test_stable_ties_and_leading_zero_ids(client):
    data = (
        "record_id,timestamp,customer_id,terminal_id,amount\n"
        "0002,2026-02-01T00:00:00,01,02,20\n"
        "0001,2026-02-01T00:00:00,01,02,20\n"
    ).encode()
    response = upload(client, data, history=False)
    assert response.status_code == 200
    rows = response.json()["operations"]
    assert [r["record_id"] for r in rows] == ["0002", "0001"]
    assert rows[0]["score"] == rows[1]["score"]
    assert all(r["customer_id"] == "01" and r["terminal_id"] == "02" for r in rows)


@pytest.mark.parametrize("field", ["target", "label", "TX_FRAUD", "TX_FRAUD_SCENARIO", "customer_count_30d"])
def test_targets_cannot_enter_features(client, app, monkeypatch, field):
    frame = pl.read_csv(io.BytesIO(csv_data())).with_columns(pl.lit(1).alias(field))

    def forbidden(*args, **kwargs):
        pytest.fail("Invalid labeled input must not reach feature generation or prediction")

    with monkeypatch.context() as patch:
        patch.setattr(app.state.service.model, "analyze", forbidden)
        assert upload(client, frame.write_csv().encode()).status_code == 422
        assert upload(client, past=frame.write_csv().encode()).status_code == 422
    prepared = app.state.service.model.prepare(pl.read_csv(io.BytesIO(csv_data())))
    assert prepared.columns == FEATURES
    assert not set(prepared.columns) & {"target", "label", "TX_FRAUD", "TX_FRAUD_SCENARIO"}


def test_missing_history_is_documented_cold_start(client):
    result = upload(client, history=False)
    assert result.status_code == 200
    assert result.json()["history_count"] == 0
    assert any("No history supplied" in w for w in result.json()["warnings"])
    partial = csv_data("history").splitlines()
    response = upload(client, past=b"\n".join([partial[0], *partial[-3:]]))
    assert response.status_code == 200
    assert any("Insufficient history" in w for w in response.json()["warnings"])


def test_invalid_history_overlap_and_ids(client):
    assert upload(client, past=csv_data()).status_code == 422
    history = pl.read_csv(io.BytesIO(csv_data("history"))).with_columns(
        pl.lit("own-purchase-001").alias("record_id")
    )
    assert upload(client, past=history.head(1).write_csv().encode()).status_code == 422
    assert upload(client, past=b"").status_code == 422


def test_bad_schema_private_error_and_no_retained_data(client, caplog):
    private = "PRIVATE-FINANCIAL-VALUE"
    bad = csv_data().replace(b"32", private.encode())  # ensure a real invalid value below
    bad = bad.replace(b",34", f",{private}".encode())
    response = upload(client, bad)
    assert response.status_code == 422
    assert private not in response.text and private not in caplog.text
    assert upload(client, csv_data().replace(b"amount", b"not_amount")).status_code == 422
    assert upload(client, csv_data().replace(b"customer_id", b"record_id")).status_code == 422


@pytest.mark.parametrize(
    "filename,data,status",
    [
        ("payload.pkl", b"not a pickle", 400),
        ("bad.xlsx", b"not a zip", 400),
        ("bad.csv", b"\xff", 400),
        ("bad.csv", b"record_id,timestamp\n", 422),
    ],
)
def test_unsupported_and_corrupt_files(client, filename, data, status):
    assert upload(client, data, filename=filename).status_code == status


def test_file_and_request_limits():
    with TestClient(create_app(replace(Settings(), max_file_bytes=32))) as client:
        assert upload(client).status_code == 413
    with TestClient(create_app(replace(Settings(), max_request_bytes=128))) as client:
        assert upload(client).status_code == 413


@pytest.mark.parametrize(
    "settings",
    [
        replace(Settings(), max_transactions=2),
        replace(Settings(), max_history=2),
        replace(Settings(), max_combined_rows=10),
    ],
)
def test_row_limits(settings):
    with TestClient(create_app(settings)) as client:
        assert upload(client).status_code == 413


def test_no_content_length_stream_limit():
    app = create_app(replace(Settings(), max_request_bytes=8))
    messages = iter(
        [
            {"type": "http.request", "body": b"12345", "more_body": True},
            {"type": "http.request", "body": b"67890", "more_body": False},
        ]
    )
    sent = []

    async def run():
        async def receive():
            return next(messages)

        async def send(message):
            sent.append(message)

        await app({"type": "http", "method": "POST", "path": "/api/v1/analyze", "headers": []}, receive, send)

    asyncio.run(run())
    assert sent[0]["status"] == 413
    assert app.state.analysis_slots.acquire(blocking=False)
    app.state.analysis_slots.release()


def test_busy_during_real_analysis_and_health_still_responds(client, app, monkeypatch):
    original = app.state.service.model.analyze
    entered, release = threading.Event(), threading.Event()

    def delayed(*args, **kwargs):
        entered.set()
        assert release.wait(10)
        return original(*args, **kwargs)

    monkeypatch.setattr(app.state.service.model, "analyze", delayed)
    with ThreadPoolExecutor(max_workers=1) as pool:
        pending = pool.submit(upload, client)
        try:
            assert entered.wait(10)
            response = client.post("/api/v1/demo/analyze")
            assert response.status_code == 429 and response.headers["Retry-After"] == "1"
            assert client.get("/api/v1/health").status_code == 200
        finally:
            release.set()
        assert pending.result(timeout=10).status_code == 200


def test_internal_error_is_sanitized_and_releases_capacity(client, app, monkeypatch, caplog):
    def fail(*args, **kwargs):
        raise RuntimeError("PRIVATE-BANK-DATA")

    with monkeypatch.context() as patch:
        patch.setattr(app.state.service.model, "analyze", fail)
        response = upload(client)
        assert response.status_code == 500
        assert "PRIVATE-BANK-DATA" not in response.text + caplog.text
    assert upload(client).status_code == 200


def test_demo_downloads_and_real_pipeline(client):
    demo = client.get("/api/v1/demo").json()
    assert demo["history_count"] == 93 and "self-authored" in demo["provenance"]
    assert client.get(demo["downloads"]["transactions"]).content == csv_data()
    assert client.get(demo["downloads"]["history"]).content == csv_data("history")
    a = client.post(demo["analysis_url"], json={"top_k": 5})
    b = upload(client)
    assert a.status_code == b.status_code == 200
    assert stable(a.json()) == stable(b.json())
    assert stable(a.json()) == stable(client.post(demo["analysis_url"], json={"top_k": 5}).json())
    assert client.get("/api/v1/templates/not-a-file.csv").status_code == 404
    assert client.post(demo["analysis_url"], json={"top_k": True}).status_code == 422


def test_xlsx_formula_links_entities_and_bombs(client):
    book = Workbook()
    book.active.append(RAW_COLUMNS)
    book.active.append(
        ["id", "2026-02-01T00:00:00", "customer", "terminal", '=WEBSERVICE("https://example.com")']
    )
    stream = io.BytesIO()
    book.save(stream)
    assert upload(client, stream.getvalue(), filename="formula.xlsx").status_code == 400
    book.active["E2"] = 1
    book.active["A2"].hyperlink = "https://example.com"
    stream = io.BytesIO()
    book.save(stream)
    book.close()
    assert upload(client, stream.getvalue(), filename="link.xlsx").status_code == 400
    for content, status in [(b"0" * 1_000_000, 413), (b'<!DOCTYPE x [<!ENTITY y "attack">]><x>&y;</x>', 400)]:
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("xl/worksheets/sheet1.xml", content)
        assert upload(client, stream.getvalue(), filename="unsafe.xlsx").status_code == status


def test_multipart_handles_closed_on_success_failure_and_truncation(client, monkeypatch):
    import starlette.formparsers as parsers

    created = []
    original = parsers.SpooledTemporaryFile

    def tracked(*args, **kwargs):
        handle = original(*args, **kwargs)
        created.append(handle)
        return handle

    monkeypatch.setattr(parsers, "SpooledTemporaryFile", tracked)
    assert upload(client).status_code == 200
    assert upload(client, b"bad").status_code == 422
    assert upload(client, top_k="bad").status_code == 422
    response = client.post(
        "/api/v1/analyze",
        content=(
            b'--cut\r\nContent-Disposition: form-data; name="transactions"; filename="a.csv"\r\n\r\ndata'
        ),
        headers={"Content-Type": "multipart/form-data; boundary=cut"},
    )
    assert response.status_code in {400, 422}
    assert created and all(handle.closed and not handle._rolled for handle in created)


def test_cors_is_explicit_and_covers_errors():
    with TestClient(create_app(replace(Settings(), frontend_origin="http://localhost:5173"))) as client:
        good = client.get("/api/v1/health", headers={"Origin": "http://localhost:5173"})
        assert good.headers["access-control-allow-origin"] == "http://localhost:5173"
        other = client.get("/api/v1/health", headers={"Origin": "https://untrusted.example"})
        assert "access-control-allow-origin" not in other.headers
        failed = client.post("/api/v1/analyze", headers={"Origin": "http://localhost:5173"})
        assert (
            failed.status_code == 400
            and failed.headers["access-control-allow-origin"] == "http://localhost:5173"
        )


def test_openapi_matches_actual_response_contract(client):
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/api/v1/analyze"]["post"]
    inputs = operation["requestBody"]["content"]["multipart/form-data"]["schema"]
    assert inputs["required"] == ["transactions", "top_k"]
    assert set(inputs["properties"]) == {"transactions", "history", "top_k"}
    assert set(schema["components"]["schemas"]["AnalyzeResponse"]["properties"]) == set(upload(client).json())


def test_config_rejects_unbounded_or_unsupported_settings(monkeypatch):
    for kwargs in [
        {"threads": 4},
        {"max_concurrent": 0},
        {"max_transactions": 1_000_001},
        {"frontend_origin": "*"},
        {"frontend_origin": "https://site.example/"},
    ]:
        with pytest.raises(ValueError):
            Settings(**kwargs)
    monkeypatch.setenv("AUDITLENS_THREADS", "1")
    assert Settings.from_env().threads == 1


def test_no_prediction_during_model_metadata(client, app, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Metadata must not recompute benchmarks")

    monkeypatch.setattr(app.state.service.model.pipeline, "predict_proba", forbidden)
    assert client.get("/api/v1/model").status_code == 200


def test_successful_model_load_happens_once(monkeypatch):
    original = HandbookService.load
    calls = []

    def counted(self):
        calls.append(self)
        return original(self)

    monkeypatch.setattr(HandbookService, "load", counted)
    with TestClient(create_app()) as client:
        assert upload(client).status_code == 200
        assert client.post("/api/v1/demo/analyze").status_code == 200
        assert client.get("/api/v1/health").status_code == 200
    assert len(calls) == 1
