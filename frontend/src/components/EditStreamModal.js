import React, { useState, useEffect } from 'react';

function EditStreamModal({ stream, onEdit, onClose, loading }) {
  const [url, setUrl] = useState('');
  const [label, setLabel] = useState('');
  const [error, setError] = useState('');

  // Initialize form with current stream data
  useEffect(() => {
    if (stream) {
      setUrl(stream.url || '');
      setLabel(stream.label || '');
      setError('');
    }
  }, [stream]);

  const validateUrl = (url) => {
    if (!url.trim()) {
      return 'URL is required';
    }
    if (!url.startsWith('rtsp://')) {
      return 'URL must start with rtsp://';
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const urlError = validateUrl(url);
    if (urlError) {
      setError(urlError);
      return;
    }

    const result = await onEdit(stream.id, {
      url: url.trim(),
      label: label.trim() || null
    });

    if (result.success) {
      onClose();
    } else {
      setError(result.error);
    }
  };

  const handleCancel = () => {
    onClose();
  };

  if (!stream) return null;

  return (
    <div className="modal-backdrop" onClick={handleCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Edit Stream</h2>
          <button className="modal-close" onClick={handleCancel}>
            ✕
          </button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">RTSP URL *</label>
            <input
              type="text"
              className={`form-input ${error ? 'error' : ''}`}
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="rtsp://username:password@host:port/path"
              disabled={loading}
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Label (Optional)</label>
            <input
              type="text"
              className="form-input"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              placeholder="e.g., Front Door Camera"
              disabled={loading}
            />
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <div className="modal-actions">
            <button
              type="button"
              className="button secondary"
              onClick={handleCancel}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="button primary"
              disabled={loading || !url.trim()}
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EditStreamModal;
