#!/bin/bash

# Start the Streamlit web UI in headless mode
echo "Starting Tashkeel Web UI in headless mode..."
streamlit run api/web_ui.py --server.headless=true --server.port=8501 --server.address=0.0.0.0
