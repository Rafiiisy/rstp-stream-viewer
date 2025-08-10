# RTSPViewer Frontend

React frontend for the RTSP Stream Viewer application with real-time video streaming capabilities.

## Features

- **Add RTSP Streams** - Input field for RTSP URLs with optional labels
- **Real-time Video Streaming** - Live video display using WebSocket and JSMpeg
- **Responsive Grid Layout** - Automatic grid adjustment for multiple streams
- **Stream Controls** - Play/Pause/Stop controls for each stream
- **Error Handling** - Status indicators and retry functionality
- **Persistent Storage** - Streams saved to localStorage
- **Professional UI** - Clean blue and white theme

## Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend server running on localhost:8000

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The application will open at `http://localhost:3000`

## Usage

### Adding Streams
1. Enter an RTSP URL in the "RTSP URL" field
2. Optionally add a label for the stream
3. Click "Add Stream"

### Controlling Streams
- **Play** - Start streaming video
- **Stop** - Stop the stream
- **Retry** - Reconnect after errors
- **Remove** - Remove stream from grid

### Example RTSP URL
```
rtsp://admin:admin123@49.248.155.178:555/cam/realmonitor?channel=1&subtype=0
```

## Technical Details

### Components
- `App.js` - Main application component
- `Header.js` - Application header with logo
- `AddStreamForm.js` - Form for adding new streams
- `StreamGrid.js` - Grid layout for stream tiles
- `StreamTile.js` - Individual stream tile with video player

### Technologies
- **React 18** - UI framework
- **JSMpeg** - Video player for MPEG-TS streams
- **WebSocket** - Real-time communication with backend
- **CSS Grid** - Responsive layout

### API Integration
- **POST /api/streams/** - Add new stream
- **GET /api/streams/** - List all streams
- **DELETE /api/streams/{id}/** - Remove stream
- **WebSocket /ws/stream?id={id}** - Video streaming

## Development

### Available Scripts
- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Project Structure
```
src/
├── components/
│   ├── Header.js
│   ├── AddStreamForm.js
│   ├── StreamGrid.js
│   └── StreamTile.js
├── App.js
├── App.css
├── index.js
└── index.css
```

## Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Ensure the Django backend is running on port 8000
   - Check that CORS is properly configured

2. **Video Not Playing**
   - Verify the RTSP URL is accessible
   - Check browser console for WebSocket errors
   - Ensure FFmpeg is installed on the backend

3. **JSMpeg Not Loading**
   - Check internet connection (CDN dependency)
   - Verify the script tag in index.html

### Browser Compatibility
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Deployment

### Build for Production
```bash
npm run build
```

### Static Hosting
The built application can be deployed to:
- GitHub Pages
- Netlify
- Vercel
- Any static hosting service

### Environment Variables
- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:8000)
- `REACT_APP_WS_URL` - WebSocket URL (default: ws://localhost:8000)
