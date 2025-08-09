# RTSP Stream Viewer - Backend

Django backend with Channels for handling RTSP video streams and WebSocket connections.

## Features

- REST API for managing RTSP streams
- WebSocket support for real-time video streaming
- FFmpeg integration for RTSP to MPEG-TS conversion
- Support for multiple concurrent streams
- Error handling and status reporting

## Prerequisites

- Python 3.11+
- FFmpeg (for RTSP processing)
- Docker (optional)

## Installation

### Local Development

#### Option 1: Using Startup Scripts (Recommended)

**Windows:**
```bash
start_dev.bat
```

**Linux/Mac:**
```bash
chmod +x start_dev.sh
./start_dev.sh
```

#### Option 2: Manual Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver 0.0.0.0:8000
```

#### Testing the Backend

Run the test script to verify everything is working:
```bash
python test_backend.py
```

### Docker

1. Build the image:
```bash
docker build -t rtsp-backend .
```

2. Run the container:
```bash
docker run -p 8000:8000 rtsp-backend
```

## API Endpoints

### REST API

- `GET /api/health/` - Health check
- `GET /api/streams/` - List all streams
- `POST /api/streams/` - Create a new stream
- `GET /api/streams/{id}/` - Get stream details
- `DELETE /api/streams/{id}/` - Delete a stream

### WebSocket

- `ws://localhost:8000/ws/stream?id={stream_id}` - Connect to stream by ID
- `ws://localhost:8000/ws/stream?url={rtsp_url}` - Connect to stream by URL

## WebSocket Messages

### Inbound (Client → Server)
```json
{"action": "start"}     // Start streaming
{"action": "stop"}      // Stop streaming
{"action": "reconnect"} // Reconnect stream
```

### Outbound (Server → Client)
```json
// Status updates
{"type": "status", "phase": "connecting|playing|stopped|connected"}

// Error messages
{"type": "error", "code": "AUTH|NOT_FOUND|TIMEOUT", "message": "..."}
```

// Binary video data (MPEG-TS format)

## Environment Variables

- `FFMPEG_TIMEOUT` - FFmpeg timeout in seconds (default: 10)
- `MAX_CONCURRENT_STREAMS` - Maximum concurrent streams (default: 10)
- `MAX_STREAMS_PER_CLIENT` - Maximum streams per client (default: 5)

## Testing

Use the provided test RTSP stream:
```
rtsp://admin:admin123@49.248.155.178:555/cam/realmonitor?channel=1&subtype=0
```

## Security Notes

- CORS is enabled for all origins in development
- RTSP credentials are masked in logs
- Rate limiting should be implemented for production
- Use HTTPS/WSS in production
