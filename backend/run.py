"""Entry point for running the Swallowtail backend."""

import logging
import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

from src.core.config import get_settings


def setup_logging() -> None:
    """Configure logging for the application."""
    settings = get_settings()
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main() -> None:
    """Run the FastAPI application."""
    setup_logging()
    settings = get_settings()
    
    logging.info(f"Starting Swallowtail API on {settings.api_host}:{settings.api_port}")
    
    uvicorn.run(
        "src.api.main:socket_app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()