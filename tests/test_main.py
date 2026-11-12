import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    with TestClient(app) as c:
        yield c


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_redirect(client):
    r = client.post("/links", json={"url": "https://example.com/page"})
    assert r.status_code == 201
    code = r.json()["code"]
    redirect = client.get(f"/{code}", follow_redirects=False)
    assert redirect.status_code == 307
    assert redirect.headers["location"] == "https://example.com/page"


def test_stats_count_clicks(client):
    code = client.post("/links", json={"url": "https://example.com"}).json()["code"]
    client.get(f"/{code}", follow_redirects=False)
    client.get(f"/{code}", follow_redirects=False)
    assert client.get(f"/links/{code}/stats").json()["clicks"] == 2


def test_invalid_url_rejected(client):
    assert client.post("/links", json={"url": "not-a-url"}).status_code == 422


def test_unknown_code_404(client):
    assert client.get("/nope123", follow_redirects=False).status_code == 404
