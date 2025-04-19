import hoh_parser.api.jsonrpc
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager

import base64
import tempfile

import types

@pytest_asyncio.fixture
async def test_app(monkeypatch):
    import aiojobs
    dummy_scheduler = types.SimpleNamespace(
        spawn=lambda *a, **k: None,
        close=lambda *a, **k: None,
        wait_closed=lambda *a, **k: None,
        _closed=False,
        _failed_task=None,
    )
    monkeypatch.setattr(aiojobs, "create_scheduler", lambda *a, **k: dummy_scheduler)
    from hoh_parser.api.jsonrpc import get_jsonrpc_router
    app = FastAPI()
    app.mount("/jsonrpc", get_jsonrpc_router())
    async with LifespanManager(app):
        yield app

@pytest_asyncio.fixture
async def async_client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac



@pytest.mark.asyncio
async def test_health_check(async_client):
    payload = {
        "jsonrpc": "2.0",
        "method": "health_check",
        "params": {},
        "id": 1
    }
    response = await async_client.post("/jsonrpc/", json=payload)
    assert response.status_code == 200
    data = response.json()
    if "result" not in data:
        print("DEBUG: response.json() =", data)
    assert data["result"]["status"] == "ok"
    assert "server_time" in data["result"]

@pytest.mark.asyncio
async def test_get_capabilities(async_client):
    payload = {
        "jsonrpc": "2.0",
        "method": "get_capabilities",
        "params": {},
        "id": 2
    }
    response = await async_client.post("/jsonrpc/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["jsonrpc"] == "2.0"
    assert "server" in data["result"]
    assert "capabilities" in data["result"]

@pytest.mark.asyncio
async def test_parse_file(async_client):
    code = """def foo(x):\n    return x + 1\n"""
    b64_content = base64.b64encode(code.encode()).decode()
    payload = {
        "jsonrpc": "2.0",
        "method": "parse_file",
        "params": {"filename": "foo.py", "content_b64": b64_content},
        "id": 3
    }
    response = await async_client.post("/jsonrpc/", json=payload)
    data = response.json()
    print("DEBUG: response.json() =", data)
    assert response.status_code == 200
    assert "functions" in data["result"]
    assert any(f["name"] == "foo" for f in data["result"]["functions"])

@pytest.mark.asyncio
async def test_symbol_table(async_client):
    code = """def bar(y):\n    return y * 2\n"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(code.encode())
        tmp.flush()
        tmp_path = tmp.name
    payload = {
        "jsonrpc": "2.0",
        "method": "symbol_table",
        "params": {"filepath": tmp_path},
        "id": 4
    }
    response = await async_client.post("/jsonrpc/", json=payload)
    data = response.json()
    print("DEBUG: response.json() =", data)
    assert response.status_code == 200
    assert "functions" in data["result"]
    assert any(f["name"] == "bar" for f in data["result"]["functions"])
