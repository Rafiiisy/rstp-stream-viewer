import React from 'react';
import StreamTile from './StreamTile';

function StreamGrid({ streams, onRemoveStream, onLoadSavedStreams, loading }) {
  return (
    <div>
      <div className="stream-grid-header">
        <h2>Streams ({streams.length})</h2>
        <button 
          className="refresh-button"
          onClick={onLoadSavedStreams}
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
      
      <div className="stream-grid">
        {streams.map((stream) => (
          <StreamTile
            key={stream.id}
            stream={stream}
            onRemove={onRemoveStream}
          />
        ))}
      </div>
    </div>
  );
}

export default StreamGrid;
