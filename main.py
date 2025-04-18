from fastapi import FastAPI
from HoH_parser.api.routes import router
from HoH_parser.api.jsonrpc import jsonrpc_router
from HoH_parser.config import settings
from HoH_parser.utils.logging import get_logger

logger = get_logger("HoH_parser.main")

app = FastAPI(title="Hammer of Hephaestus MCP Server")
app.include_router(router)
app.include_router(jsonrpc_router)

@app.on_event("startup")
def startup_event() -> None:
    logger.info("Starting HoH MCP Server with log level: %s", settings.log_level)
    if settings.debug:
        logger.debug("Debug mode is enabled.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
