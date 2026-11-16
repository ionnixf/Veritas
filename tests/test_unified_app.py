"""The production UI shares an origin without exposing local research files."""

import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize("built", [True, False])
def test_static_build_is_optional_and_confined(tmp_path, monkeypatch, built):
    module = importlib.import_module("auditlens.backend.app")
    dist = tmp_path / "frontend/dist"
    dist.mkdir(parents=True)
    (tmp_path / "private.txt").write_text("private research records")
    if built:
        (dist / "index.html").write_text("<!doctype html><title>AuditLens</title>")
        (dist / "app.js").write_text("console.log('local build')")
        (dist / "escape.txt").symlink_to(tmp_path / "private.txt")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    with TestClient(module.create_app()) as client:
        root = client.get("/")
        assert root.status_code == (200 if built else 404)
        if built:
            assert root.headers["content-type"].startswith("text/html")
            assert "AuditLens" in root.text
            assert client.get("/app.js").status_code == 200
        assert client.get("/api/v1/health").json()["device"] == "cpu"
        assert client.get("/api/v1/templates/transactions.csv").status_code == 200
        for path in ("/models/registry.json", "/data/raw/", "/private.txt", "/escape.txt", "/api/v1/missing"):
            response = client.get(path)
            assert response.status_code == 404
            assert "private research records" not in response.text
