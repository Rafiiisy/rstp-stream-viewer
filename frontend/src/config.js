// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_ENDPOINT 
  ? `https://${process.env.REACT_APP_API_ENDPOINT}` 
  : 'http://localhost:8000';

const WS_BASE_URL = process.env.REACT_APP_API_ENDPOINT 
  ? `wss://${process.env.REACT_APP_API_ENDPOINT}` 
  : 'ws://localhost:8000';

// Generate unique client ID for each stream instance
const generateClientId = () => {
  return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

export const config = {
  API_BASE_URL,
  WS_BASE_URL,
  generateClientId,
  API_ENDPOINTS: {
    STREAMS: `${API_BASE_URL}/api/streams/`,
    HEALTH: `${API_BASE_URL}/api/health/`,
    THUMBNAIL: (streamId) => `${API_BASE_URL}/api/streams/${streamId}/thumbnail/`,
    THUMBNAIL_REFRESH: (streamId) => `${API_BASE_URL}/api/streams/${streamId}/thumbnail/refresh/`,
    THUMBNAIL_CACHE_STATS: `${API_BASE_URL}/api/thumbnails/cache/stats/`,
  },
  WS_ENDPOINTS: {
    STREAM: (id, videoOnly = false, clientId = null) => {
      const baseUrl = `${WS_BASE_URL}/ws/stream?id=${id}&video_only=${videoOnly}`;
      return clientId ? `${baseUrl}&client_id=${clientId}` : baseUrl;
    },
  }
};

export default config;
