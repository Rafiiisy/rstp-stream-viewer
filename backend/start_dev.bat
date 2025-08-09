@echo off
echo Starting RTSP Stream Viewer Backend (Development Mode)...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run migrations
echo Running database migrations...
python manage.py migrate

REM Start the server with Daphne for WebSocket support
echo Starting Django server with Daphne (WebSocket support)...
python -m daphne config.asgi:application --port 8000 --bind 0.0.0.0
