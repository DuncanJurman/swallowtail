"""Celery worker entry point."""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.core.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start()