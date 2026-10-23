from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_index_returns_app_info():
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["app"] == "python-app"
    assert "version" in body
    assert "pod" in body


def test_healthz_ok():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_unknown_path_returns_404():
    assert client.get("/not-exist").status_code == 404
