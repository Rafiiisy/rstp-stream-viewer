#!/bin/bash

# RTSP Stream Viewer Backend Startup Script (Development Mode)

echo "Starting RTSP Stream Viewer Backend (Development Mode)..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Start the server with Daphne for WebSocket support
echo "Starting Django server with Daphne (WebSocket support)..."
python -m daphne config.asgi:application --port ${PORT:-8000} --bind 0.0.0.0
