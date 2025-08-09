# RTSP Stream Viewer

A real-time RTSP stream viewing application with a modern web interface for monitoring multiple IP cameras simultaneously. Built with Django Channels for WebSocket streaming and React for the frontend interface.

Access it here:
https://rstp-stream-viewer.vercel.app/

![RTSP Stream Viewer Preview](frontend/public/preview.png)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Overview

The RTSP Stream Viewer is a full-stack web application that allows users to:
- Add and manage multiple RTSP stream URLs
- View live video streams in a responsive grid layout
- Control individual streams (play, pause, stop)
- Generate thumbnails for paused streams
- Handle connection errors and retry mechanisms

The application uses FFmpeg to transcode RTSP streams to MPEG-TS format for web playback via JSMpeg, with Django Channels handling WebSocket connections for real-time video streaming.

## Features

### Core Functionality
- **Multi-stream Support**: View multiple RTSP streams simultaneously in a responsive grid
- **Real-time Streaming**: Live video streaming via WebSocket connections
- **Stream Management**: Add, edit, and remove RTSP streams with custom labels
- **Playback Controls**: Play, pause, and stop individual streams
- **Error Handling**: Robust error handling with retry mechanisms
- **Thumbnail Generation**: Automatic thumbnail generation for paused streams

### User Interface
- **Responsive Design**: Works on desktop and mobile devices
- **Grid Layout**: Automatic responsive grid that adapts to screen size
- **Stream Expansion**: Click to expand streams for larger viewing
- **Status Indicators**: Real-time status updates (connecting, playing, error)
- **Loading States**: Visual feedback during stream operations

### Technical Features
- **WebSocket Streaming**: Efficient binary video streaming
- **FFmpeg Integration**: RTSP to MPEG-TS transcoding
- **Connection Pooling**: Shared FFmpeg processes for multiple viewers
- **Caching**: Thumbnail caching for improved performance
- **Cross-origin Support**: CORS configuration for deployment

## Architecture

### Backend Architecture (Django + Channels)

The backend is built with Django and Django Channels, providing both REST API endpoints and WebSocket streaming capabilities.

#### Key Components:

**Models** (`backend/streams/models.py`):
- `Stream`: Stores RTSP URLs, labels, and metadata
- URL validation for RTSP format
- Automatic WebSocket URL generation

**Views** (`backend/streams/views.py`):
- REST API endpoints for CRUD operations
- RTSP URL validation using FFmpeg
- Thumbnail generation and caching
- Health check endpoints

**WebSocket Consumer** (`backend/streams/consumers.py`):
- `StreamConsumer`: Handles WebSocket connections
- `StreamManager`: Manages shared FFmpeg processes
- `StreamInfo`: Per-stream state management
- Binary video streaming to multiple clients

**FFmpeg Helper** (`backend/streams/ffmpeg_helper.py`):
- `FFmpegProcess`: Manages FFmpeg subprocesses
- RTSP to MPEG-TS transcoding
- Error handling and process lifecycle management

**Thumbnail Service** (`backend/streams/thumbnail_service.py`):
- Automatic thumbnail generation from RTSP streams
- Caching system with TTL
- Base64 encoding for web delivery

#### Backend Flow:

1. **Stream Addition**:
   ```
   POST /api/streams/ → validate RTSP URL → create Stream object → return with WebSocket URL
   ```

2. **WebSocket Connection**:
   ```
   WS /ws/stream?id=<uuid> → authenticate → join StreamManager → start FFmpeg process
   ```

3. **Video Streaming**:
   ```
   FFmpeg RTSP → MPEG-TS → WebSocket binary data → JSMpeg player
   ```

4. **Stream Control**:
   ```
   WS message → StreamManager → FFmpeg process control → status response
   ```

### Frontend Architecture (React)

The frontend is built with React and provides a modern, responsive interface for stream management.

#### Key Components:

**App** (`frontend/src/App.js`):
- Main application state management
- Stream CRUD operations via API
- Loading state management

**StreamGrid** (`frontend/src/components/StreamGrid.js`):
- Responsive grid layout for streams
- Refresh functionality
- Empty state handling

**StreamTile** (`frontend/src/components/StreamTile.js`):
- Individual stream display and controls
- WebSocket connection management
- JSMpeg player integration
- Play/pause/stop controls
- Error handling and retry logic

**AddStreamForm** (`frontend/src/components/AddStreamForm.js`):
- RTSP URL input and validation
- Stream label management
- Form submission handling

**StreamThumbnail** (`frontend/src/components/StreamThumbnail.js`):
- Thumbnail display for paused streams
- Caching and refresh functionality

#### Frontend Flow:

1. **Stream Addition**:
   ```
   Form input → API call → update state → add to grid
   ```

2. **Stream Playback**:
   ```
   Play button → WebSocket connection → JSMpeg initialization → video display
   ```

3. **Stream Control**:
   ```
   Control button → WebSocket message → backend action → UI update
   ```

## Prerequisites

### System Requirements
- Python 3.8+
- Node.js 16+
- FFmpeg (must be installed and available in PATH)
- Git

### FFmpeg Installation

**Windows:**
```bash
# Download from https://ffmpeg.org/download.html
# Add to PATH environment variable
```

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**CentOS/RHEL:**
```bash
sudo yum install ffmpeg
```

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Rafiiisy/rstp-stream-viewer
cd SkylarkTest2
```

### 2. Backend Setup

#### Option A: Manual Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

#### Option B: Using Development Scripts (Recommended)

**Windows:**
```bash
cd backend
start_dev.bat
```

**macOS/Linux:**
```bash
cd backend
chmod +x start_dev.sh
./start_dev.sh
```

**Note:** The development scripts automatically:
- Create virtual environment if it doesn't exist
- Install dependencies
- Run database migrations
- Start the server with Daphne (WebSocket support)
- Use port 8000 by default (configurable via PORT environment variable)

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 4. Environment Configuration

Create environment variables for production deployment:

**Frontend** (`frontend/.env.local`):
```env
REACT_APP_API_ENDPOINT=https://rstp-stream-viewer.vercel.app/
or for local testing
REACT_APP_API_ENDPOINT=http://localhost:8000
```

## Usage

### Accessing the Application

1. **Local Development**:
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000
   - API: http://localhost:8000/api/

2. **Production**:
   - Frontend: https://rstp-stream-viewer.vercel.app/
   - Backend: https://rstp-stream-viewer-production.up.railway.app

### Adding Streams

1. Open the application in your web browser
2. Enter an RTSP URL in the "Add Stream" form
3. Optionally add a label for the stream
4. Click "Add Stream"
5. The stream will be validated and added to the grid

### Managing Streams

- **Play**: Click the play button to start streaming
- **Pause**: Hover over a playing stream and click the pause button
- **Stop**: Click the stop button to end the stream
- **Edit**: Click the edit button to modify stream details
- **Remove**: Click the remove button to delete the stream
- **Expand**: Click the expand button for larger viewing

### Example RTSP URLs

```
rtsp://admin:admin123@49.248.155.178:555/cam/realmonitor?channel=1&subtype=0 (project test case)
rtsp://192.168.1.100:554/stream1
rtsp://admin:password@192.168.1.101:554/h264Preview_01_main
rtsp://fake-camera-1.local:554/stream1
```

## API Documentation

### REST Endpoints

#### Streams

**GET** `/api/streams/`
- List all active streams
- Returns: Array of stream objects

**POST** `/api/streams/`
- Create a new stream
- Body: `{"url": "rtsp://...", "label": "Camera 1"}`
- Returns: Created stream object

**GET** `/api/streams/{id}/`
- Get stream details
- Returns: Stream object

**PUT** `/api/streams/{id}/`
- Update stream
- Body: `{"url": "rtsp://...", "label": "Updated Label"}`
- Returns: Updated stream object

**DELETE** `/api/streams/{id}/`
- Soft delete stream (sets is_active=False)
- Returns: 204 No Content

#### Thumbnails

**GET** `/api/streams/{id}/thumbnail/`
- Get stream thumbnail
- Query params: `refresh=true` to force refresh
- Returns: Thumbnail data URL

**POST** `/api/streams/{id}/thumbnail/refresh/`
- Force refresh thumbnail
- Returns: Success message

**GET** `/api/thumbnails/cache/stats/`
- Get thumbnail cache statistics
- Returns: Cache stats

**POST** `/api/thumbnails/cache/clear/`
- Clear all thumbnail cache
- Returns: Success message

#### Health

**GET** `/api/health/`
- Health check endpoint
- Returns: `{"status": "healthy"}`

### WebSocket Endpoints

#### Stream WebSocket

**URL**: `ws://localhost:8000/ws/stream?id={stream_id}&video_only={true|false}&client_id={client_id}`

**Parameters**:
- `id`: Stream UUID (required)
- `video_only`: Boolean for JSMpeg connections (optional)
- `client_id`: Unique client identifier (optional)

**Control Messages** (JSON):
```json
{"action": "start"}
{"action": "stop"}
{"action": "reconnect"}
```

**Status Messages** (JSON):
```json
{"type": "status", "phase": "connecting|playing|stopped|ended"}
{"type": "error", "code": "FFMPEG_EXIT|AUTH|NOT_FOUND|TIMEOUT", "message": "..."}
{"type": "video_start"}
```

**Binary Data**: MPEG-TS video chunks (for video_only connections)

## Deployment

### Railway Deployment

The application includes Railway configuration files for easy deployment:

1. **Backend** (`backend/railway.json`):
   - Automatic deployment configuration
   - Environment variable setup
   - Build and start commands

### Docker Deployment

**Backend Dockerfile** (`backend/Dockerfile`):
```dockerfile
FROM python:3.9-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Run migrations and start server
CMD python manage.py migrate && daphne config.asgi:application --port $PORT --bind 0.0.0.0
```


## Troubleshooting

### Common Issues

**FFmpeg Not Found**:
```bash
# Ensure FFmpeg is installed and in PATH
ffmpeg -version
```

**WebSocket Connection Failed**:
- Check CORS settings in `backend/config/settings.py`
- Verify WebSocket URL format
- Check firewall settings

**Stream Not Playing**:
- Verify RTSP URL is accessible
- Check FFmpeg process logs
- Ensure stream format is supported

**Thumbnail Generation Failed**:
- Check FFmpeg installation
- Verify RTSP URL accessibility
- Check temporary file permissions

### Logging

Enable debug logging by setting `DEBUG=True` in environment variables.

**Backend Logs**:
```bash
python manage.py runserver --verbosity=2
```

**Frontend Logs**:
- Open browser developer tools
- Check Console tab for errors

### Performance Optimization

1. **Stream Limits**: Configure `MAX_CONCURRENT_STREAMS` in settings
2. **Thumbnail Caching**: Adjust `cache_ttl` in thumbnail service
3. **FFmpeg Quality**: Modify quality settings in `ffmpeg_helper.py`
4. **WebSocket Buffering**: Adjust buffer sizes for network conditions

### Security Considerations

1. **RTSP Authentication**: Use secure RTSP URLs with authentication
2. **CORS Configuration**: Restrict allowed origins in production
3. **Secret Key**: Use strong secret key in production
4. **Input Validation**: All RTSP URLs are validated before processing
5. **Rate Limiting**: Implement rate limiting for API endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request
