import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastmcp.utilities.lifespan import combine_lifespans

from config import settings
from utilities.logging import setup_logging

from mcp_server.tools import info_mcp

setup_logging()
logger = logging.getLogger("mcp.server")

logger.info("Generating FastMCP Starlette ASGI sub-application...")
mcp_app = info_mcp.http_app(transport="sse")


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """
    FastAPI portal core lifespan (runs in tandem with the mounted MCP lifespan).
    """
    logger.info("Initializing global FastAPI app lifespan...")
    yield
    logger.info("Global FastAPI teardown complete.")


combined_lifespan = combine_lifespans(app_lifespan, mcp_app.lifespan)

app = FastAPI(title=settings.app_name, lifespan=combined_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/mcp", mcp_app)
logger.info("MCP server successfully mounted at '/mcp'.")


@app.get("/health", tags=["Monitoring"])
async def health_check():
    """
    Provides real-time health diagnostics of the FastAPI app and the mounted MCP server.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "app": settings.app_name,
            "environment": settings.environment,
            "mounted_servers": {
                "mcp": {
                    "status": "online",
                    "tools_count": len(await info_mcp.list_tools()),
                }
            },
        },
        status_code=200,
    )


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}!",
        "health_endpoint": "/health",
        "mcp_endpoint": "/mcp/sse/",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("mcp_server.server:app", host="127.0.0.1", port=8000, reload=True)
