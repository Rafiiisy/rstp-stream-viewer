// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_ENDPOINT 
  ? `https://${process.env.REACT_APP_API_ENDPOINT}` 
  : 'http://localhost:8000';

const WS_BASE_URL = process.env.REACT_APP_API_ENDPOINT 
  ? `wss://${process.env.REACT_APP_API_ENDPOINT}` 
  : 'ws://localhost:8000';

export const config = {
  API_BASE_URL,
  WS_BASE_URL,
  API_ENDPOINTS: {
    STREAMS: `${API_BASE_URL}/api/streams/`,
    HEALTH: `${API_BASE_URL}/api/health/`,
  },
  WS_ENDPOINTS: {
    STREAM: (id, videoOnly = false) => 
      `${WS_BASE_URL}/ws/stream?id=${id}&video_only=${videoOnly}`,
  }
};

export default config;
