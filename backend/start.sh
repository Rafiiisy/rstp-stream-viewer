#!/bin/bash

# Wait for database to be ready (if using external database)
echo "Starting RTSP Stream Viewer Backend..."

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files (if needed)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the server
echo "Starting Daphne server on port $PORT..."
daphne -b 0.0.0.0 -p $PORT config.asgi:application
