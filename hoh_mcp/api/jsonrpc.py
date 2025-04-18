from fastapi_jsonrpc import JsonRpcRouter, RpcMethodParams
from HoH_parser.core.parser import parse_python_file
from HoH_parser.core.models import MCPFile
from pydantic import BaseModel
import tempfile
import base64

jsonrpc_router = JsonRpcRouter(prefix="/jsonrpc")

@jsonrpc_router.method()
def health_check() -> dict:
    """MCP-compliant health check method."""
    return {"status": "ok", "server_time": __import__('datetime').datetime.utcnow().isoformat() + 'Z'}

@jsonrpc_router.method()
def get_capabilities() -> dict:
    """MCP-compliant capability negotiation method."""
    return {
        "jsonrpc": "2.0",
        "server": "Hammer of Hephaestus MCP Server",
        "version": "0.1.0",
        "capabilities": [
            "parse_file",
            "symbol_table",
            "health_check",
            "get_capabilities"
        ],
        "resource_types": [
            "python",
            "markdown",
            "pdf",
            "web",
            "yaml",
            "json",
            "toml",
            "xml"
        ]
    }

class ParseFileParams(BaseModel):
    filename: str
    content_b64: str  # base64-encoded file content

@jsonrpc_router.method()
def parse_file(params: ParseFileParams) -> MCPFile:
    # Decode and write the file to a temp file
    content = base64.b64decode(params.content_b64)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    result = parse_python_file(tmp_path)
    return result

class SymbolTableParams(BaseModel):
    filepath: str

@jsonrpc_router.method()
def symbol_table(params: SymbolTableParams) -> dict:
    result = parse_python_file(params.filepath)
    return result.model_dump()
