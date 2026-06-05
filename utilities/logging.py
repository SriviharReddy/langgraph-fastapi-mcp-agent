import logging
import sys

from config import settings


def setup_logging() -> None:
    """
    Sets up unified logging formatting and levels across standard library logs,
    FastAPI (Uvicorn), and the mounted FastMCP servers.
    """
    # Resolve log level from settings
    level_name = settings.log_level.upper()
    log_level = getattr(logging, level_name, logging.INFO)

    # Detailed format for development, can be customized for production JSON formats
    log_format = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("app.log")],
        force=True,  # Clear existing handlers
    )

    logger = logging.getLogger("utils.logging")
    logger.info(f"Logging initialized with level: {level_name}")
