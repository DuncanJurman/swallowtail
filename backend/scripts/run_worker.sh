#!/bin/bash

# Run Celery worker for development
cd /Users/duncanjurman/Desktop/Swallowtail/backend

# Load environment variables
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Run worker with info logging using Poetry
poetry run celery -A src.core.celery_app:celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --queues=default,agents,background