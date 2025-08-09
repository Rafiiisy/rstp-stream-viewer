import React, { useState } from 'react';
import StreamTile from './StreamTile';
import { config } from '../config';

function StreamGrid({ streams, onRemoveStream, onEditStream, onLoadSavedStreams, loading }) {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = async () => {
    try {
      // Clear thumbnail cache first
      await fetch(config.API_ENDPOINTS.THUMBNAIL_CACHE_CLEAR, {
        method: 'POST',
      });
      console.log('Thumbnail cache cleared');
      
      // Increment refresh key to force thumbnail re-renders
      setRefreshKey(prev => prev + 1);
    } catch (error) {
      console.error('Error clearing thumbnail cache:', error);
    }
    
    // Then refresh streams (this will trigger thumbnail reloads)
    onLoadSavedStreams();
  };

  return (
    <div>
      <div className="stream-grid-header">
        <h2>Streams ({streams.length})</h2>
        <button 
          className="refresh-button"
          onClick={handleRefresh}
          disabled={loading}
        >
          {loading ? 'Loading...' : '↻ Refresh'}
        </button>
      </div>
      
      {loading && streams.length === 0 && (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading streams...</p>
        </div>
      )}
      
      {!loading && streams.length === 0 && (
        <div className="empty-state">
          <div className="empty-state-content">
            <h3>No Streams Added</h3>
            <p>Add an RTSP stream URL above to get started</p>
            <div className="example-url">
              <strong>Example:</strong> rtsp://fake-camera-1.local:554/stream1
            </div>
          </div>
        </div>
      )}
      
      {streams.length > 0 && (
        <div className="stream-grid">
          {streams.map((stream) => (
            <StreamTile
              key={`${stream.id}-${refreshKey}`}
              stream={stream}
              onRemove={onRemoveStream}
              onEdit={onEditStream}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default StreamGrid;
