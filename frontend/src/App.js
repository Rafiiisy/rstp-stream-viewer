import React, { useState, useEffect } from 'react';
import './App.css';
import StreamGrid from './components/StreamGrid';
import AddStreamForm from './components/AddStreamForm';
import Header from './components/Header';
import { NotificationProvider, useNotification } from './context/NotificationContext';
import { config } from './config';

function AppContent() {
  const [streams, setStreams] = useState([]);
  const [loading, setLoading] = useState(false);
  const { showSuccess, showError } = useNotification();

  // Load streams from backend on component mount
  useEffect(() => {
    loadSavedStreams();
  }, []);

  // Note: Streams are now managed by the backend API, no need for localStorage

  const addStream = async (streamData) => {
    setLoading(true);
    try {
      const response = await fetch(config.API_ENDPOINTS.STREAMS, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(streamData),
      });

      if (response.ok) {
        const newStream = await response.json();
        setStreams(prevStreams => [...prevStreams, newStream]);
        showSuccess('Stream added successfully');
        return { success: true };
      } else {
        const errorData = await response.json();
        const errorMessage = errorData.error || 'Failed to add stream';
        showError(errorMessage);
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      console.error('Error adding stream:', error);
      const errorMessage = 'Network error. Please check if the backend is running.';
      showError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const removeStream = async (streamId) => {
    try {
      const response = await fetch(`${config.API_ENDPOINTS.STREAMS}${streamId}/`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setStreams(prevStreams => prevStreams.filter(stream => stream.id !== streamId));
        showSuccess('Stream deleted successfully');
      } else {
        showError('Failed to delete stream');
        console.error('Failed to remove stream');
      }
    } catch (error) {
      console.error('Error removing stream:', error);
      showError('Network error while deleting stream');
    }
  };

  const editStream = async (streamId, streamData) => {
    setLoading(true);
    try {
      const response = await fetch(`${config.API_ENDPOINTS.STREAMS}${streamId}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(streamData),
      });

      if (response.ok) {
        const updatedStream = await response.json();
        setStreams(prevStreams => 
          prevStreams.map(stream => 
            stream.id === streamId ? updatedStream : stream
          )
        );
        showSuccess('Stream edited successfully');
        return { success: true };
      } else {
        const errorData = await response.json();
        const errorMessage = errorData.error || 'Failed to update stream';
        showError(errorMessage);
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      console.error('Error updating stream:', error);
      const errorMessage = 'Network error. Please check if the backend is running.';
      showError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const loadSavedStreams = async () => {
    setLoading(true);
    try {
      const response = await fetch(config.API_ENDPOINTS.STREAMS);
      if (response.ok) {
        const savedStreams = await response.json();
        setStreams(savedStreams);
      } else {
        showError('Failed to load streams');
      }
    } catch (error) {
      console.error('Error loading saved streams:', error);
      showError('Network error while loading streams');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <AddStreamForm onAddStream={addStream} loading={loading} />
        
        <StreamGrid 
          streams={streams} 
          onRemoveStream={removeStream}
          onEditStream={editStream}
          onLoadSavedStreams={loadSavedStreams}
          loading={loading}
        />
      </main>
    </div>
  );
}

function App() {
  return (
    <NotificationProvider>
      <AppContent />
    </NotificationProvider>
  );
}

export default App;
