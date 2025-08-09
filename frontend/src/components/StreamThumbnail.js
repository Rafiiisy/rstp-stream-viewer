import React, { useState, useEffect } from 'react';
import { config } from '../config';

function StreamThumbnail({ streamId, streamUrl, onLoad, onError, className = '', style = {} }) {
  const [thumbnail, setThumbnail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  const maxRetries = 3;
  const retryDelay = 2000; // 2 seconds

  const loadThumbnail = async (forceRefresh = false) => {
    try {
      setLoading(true);
      setError(null);

      const url = `${config.API_ENDPOINTS.STREAMS}${streamId}/thumbnail/`;
      const params = new URLSearchParams();
      if (forceRefresh) {
        params.append('refresh', 'true');
      }

      const response = await fetch(`${url}?${params}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.thumbnail) {
        setThumbnail(data.thumbnail);
        setLoading(false);
        if (onLoad) {
          onLoad(data);
        }
      } else {
        throw new Error('No thumbnail data received');
      }
    } catch (err) {
      console.error('Error loading thumbnail:', err);
      setError(err.message);
      setLoading(false);
      
      if (onError) {
        onError(err);
      }

      // Retry logic
      if (retryCount < maxRetries) {
        setTimeout(() => {
          setRetryCount(prev => prev + 1);
          loadThumbnail();
        }, retryDelay);
      }
    }
  };

  const handleRefresh = () => {
    setRetryCount(0);
    loadThumbnail(true);
  };

  useEffect(() => {
    loadThumbnail();
  }, [streamId]);

  // Loading state
  if (loading) {
    return (
      <div 
        className={`stream-thumbnail loading ${className}`}
        style={{
          ...style,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#f3f4f6',
          borderRadius: '8px',
          minHeight: '180px'
        }}
      >
        <div className="thumbnail-spinner">
          <div className="spinner"></div>
          <p>Loading thumbnail...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div 
        className={`stream-thumbnail error ${className}`}
        style={{
          ...style,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#fef2f2',
          border: '2px dashed #fca5a5',
          borderRadius: '8px',
          minHeight: '180px',
          padding: '1rem'
        }}
      >
        <div className="error-icon">📷</div>
        <p style={{ margin: '0.5rem 0', color: '#dc2626', fontSize: '0.875rem' }}>
          Failed to load thumbnail
        </p>
        <button 
          onClick={handleRefresh}
          style={{
            background: '#dc2626',
            color: 'white',
            border: 'none',
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '0.75rem'
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  // Success state
  return (
    <div 
      className={`stream-thumbnail ${className}`}
      style={{
        ...style,
        position: 'relative',
        overflow: 'hidden',
        borderRadius: '8px'
      }}
    >
      <img
        src={thumbnail}
        alt={`Thumbnail for stream ${streamId}`}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          display: 'block'
        }}
        onError={() => {
          setError('Failed to display thumbnail image');
        }}
      />
      <div 
        className="thumbnail-overlay"
        style={{
          position: 'absolute',
          top: '0',
          right: '0',
          background: 'rgba(0, 0, 0, 0.7)',
          color: 'white',
          padding: '0.25rem 0.5rem',
          fontSize: '0.75rem',
          borderRadius: '0 8px 0 8px'
        }}
      >
        📷
      </div>
    </div>
  );
}

export default StreamThumbnail;
