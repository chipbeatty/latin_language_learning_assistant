#!/bin/bash

# Kill any existing Streamlit processes
pkill -f "streamlit run" || true

# Wait for ports to be freed
sleep 1

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true

# Set environment variables
export PYTHONPATH=/Users/chip/Projects/listening_learning_app
export STREAMLIT_SERVER_RUN_ON_SAVE=true
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
export STREAMLIT_CLIENT_TOOLBAR_MODE=minimal

# Run Streamlit
streamlit run frontend/main.py
