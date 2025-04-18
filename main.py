from fastapi import FastAPI
from hoh_mcp.api.routes import router
from hoh_mcp.config import settings
from hoh_mcp.utils.logging import get_logger

logger = get_logger("hoh_mcp.main")

app = FastAPI(title="Hammer of Hephaestus MCP Server")
app.include_router(router)

@app.on_event("startup")
def startup_event() -> None:
    logger.info("Starting HoH MCP Server with log level: %s", settings.log_level)
    if settings.debug:
        logger.debug("Debug mode is enabled.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
