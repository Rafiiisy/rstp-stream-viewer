import React, { useState, useEffect } from 'react';
import './App.css';
import StreamGrid from './components/StreamGrid';
import AddStreamForm from './components/AddStreamForm';
import Header from './components/Header';

function App() {
  const [streams, setStreams] = useState([]);
  const [loading, setLoading] = useState(false);

  // Load streams from backend on component mount
  useEffect(() => {
    loadSavedStreams();
  }, []);

  // Note: Streams are now managed by the backend API, no need for localStorage

  const addStream = async (streamData) => {
    setLoading(true);
    try {
      const response = await fetch('/api/streams/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(streamData),
      });

      if (response.ok) {
        const newStream = await response.json();
        setStreams(prevStreams => [...prevStreams, newStream]);
        return { success: true };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.error || 'Failed to add stream' };
      }
    } catch (error) {
      console.error('Error adding stream:', error);
      return { success: false, error: 'Network error. Please check if the backend is running.' };
    } finally {
      setLoading(false);
    }
  };

  const removeStream = async (streamId) => {
    try {
      const response = await fetch(`/api/streams/${streamId}/`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setStreams(prevStreams => prevStreams.filter(stream => stream.id !== streamId));
      } else {
        console.error('Failed to remove stream');
      }
    } catch (error) {
      console.error('Error removing stream:', error);
    }
  };

  const loadSavedStreams = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/streams/');
      if (response.ok) {
        const savedStreams = await response.json();
        setStreams(savedStreams);
      }
    } catch (error) {
      console.error('Error loading saved streams:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <AddStreamForm onAddStream={addStream} loading={loading} />
        
        {streams.length === 0 && (
          <div className="empty-state">
            <div className="empty-state-content">
              <h3>No Streams Added</h3>
              <p>Add an RTSP stream URL above to get started</p>
              <div className="example-url">
                <strong>Example:</strong> rtsp://admin:admin123@49.248.155.178:555/cam/realmonitor?channel=1&subtype=0
              </div>
            </div>
          </div>
        )}
        
        <StreamGrid 
          streams={streams} 
          onRemoveStream={removeStream}
          onLoadSavedStreams={loadSavedStreams}
          loading={loading}
        />
      </main>
    </div>
  );
}

export default App;
