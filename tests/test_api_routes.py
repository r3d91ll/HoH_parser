import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from HoH_parser.api.routes import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_parse_file_endpoint(client):
    code = """
def foo(x):
    return x + 1
"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(code.encode())
        tmp.flush()
        tmp.seek(0)
        tmp_path = tmp.name
    with open(tmp_path, "rb") as f:
        response = client.post("/parse-file", files={"file": (os.path.basename(tmp_path), f, "text/x-python")})
    os.unlink(tmp_path)
    assert response.status_code == 200
    data = response.json()
    assert "functions" in data
    assert any(func["name"] == "foo" for func in data["functions"])

def test_symbol_table_query(client):
    code = """
def bar(y):
    return y * 2
"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(code.encode())
        tmp.flush()
        tmp_path = tmp.name
    response = client.get("/symbol-table", params={"filepath": tmp_path})
    os.unlink(tmp_path)
    assert response.status_code == 200
    data = response.json()
    assert "functions" in data
    assert any(func["name"] == "bar" for func in data["functions"])
