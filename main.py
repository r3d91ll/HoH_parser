import hoh_parser.api.jsonrpc
from fastapi import FastAPI
from hoh_parser.api.jsonrpc import get_jsonrpc_router
from hoh_parser.config import settings
from hoh_parser.utils.logging import get_logger

logger = get_logger("hoh_parser.main")

app = FastAPI(title="Hammer of Hephaestus MCP Server")
app.mount("/jsonrpc", get_jsonrpc_router())

@app.on_event("startup")
def startup_event() -> None:
    logger.info("Starting HoH MCP Server with log level: %s", settings.log_level)
    if settings.debug:
        logger.debug("Debug mode is enabled.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
