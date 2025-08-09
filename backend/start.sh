#!/bin/bash
set -e

# Run migrations
python manage.py migrate

# Start the server
exec python manage.py runserver 0.0.0.0:$PORT --noreload --insecure
