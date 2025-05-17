#!/bin/bash

# Start the FastAPI server
echo "Starting Tashkeel API server..."
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
