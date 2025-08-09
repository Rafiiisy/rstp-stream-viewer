import React, { useState } from 'react';

function AddStreamForm({ onAddStream, loading }) {
  const [url, setUrl] = useState('');
  const [label, setLabel] = useState('');
  const [error, setError] = useState('');

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

    const result = await onAddStream({
      url: url.trim(),
      label: label.trim() || null
    });

    if (result.success) {
      setUrl('');
      setLabel('');
    } else {
      setError(result.error);
    }
  };

  return (
    <div className="add-stream-form">
      <h2 className="form-title">Add RTSP Stream</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-row">
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
          <button
            type="submit"
            className="add-button"
            disabled={loading || !url.trim()}
          >
            {loading ? 'Adding...' : 'Add Stream'}
          </button>
        </div>
        {error && <div className="error-message">{error}</div>}
      </form>
    </div>
  );
}

export default AddStreamForm;
