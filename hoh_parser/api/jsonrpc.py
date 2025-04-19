from fastapi_jsonrpc import Entrypoint
from hoh_parser.core.parser import parse_python_file
from hoh_parser.core.models import MCPFile
from pydantic import BaseModel
import tempfile
import base64

from typing import Any, cast

_method_registry = []

from typing import Callable, TypeVar, Optional

F = TypeVar("F", bound=Callable)
def register_jsonrpc_method(name: Optional[str] = None) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        _method_registry.append((name or func.__name__, func))
        return func
    return decorator

@register_jsonrpc_method()
def health_check() -> dict[str, Any]:
    """MCP-compliant health check method."""
    return {"status": "ok", "server_time": __import__('datetime').datetime.utcnow().isoformat() + 'Z'}

@register_jsonrpc_method()
def get_capabilities() -> dict[str, Any]:
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

@register_jsonrpc_method()
def parse_file(filename: str, content_b64: str) -> MCPFile:
    # Decode and write the file to a temp file
    content = base64.b64decode(content_b64)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    result = parse_python_file(tmp_path)
    return result

@register_jsonrpc_method()
def symbol_table(filepath: str) -> dict[str, Any]:
    result = parse_python_file(filepath)
    return cast(dict[str, Any], result.model_dump())

def get_jsonrpc_router() -> Entrypoint:
    jsonrpc_router = Entrypoint('/')  # Mount at root of /jsonrpc
    print("DEBUG: Registered methods:", [name for name, _ in _method_registry])
    for name, func in _method_registry:
        jsonrpc_router.method(name=name)(func)
    return jsonrpc_router
