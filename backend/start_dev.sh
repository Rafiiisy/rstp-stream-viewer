#!/bin/bash

# RTSP Stream Viewer Backend Startup Script (Production Mode for Railway)

echo "Starting RTSP Stream Viewer Backend (Production Mode)..."

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Start the server with Daphne for WebSocket support
echo "Starting Django server with Daphne (WebSocket support)..."
exec python -m daphne config.asgi:application --port $PORT --bind 0.0.0.0
