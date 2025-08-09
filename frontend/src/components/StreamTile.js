import React, { useState, useEffect, useRef } from 'react';
import EditStreamModal from './EditStreamModal';
import StreamThumbnail from './StreamThumbnail';
import { config } from '../config';

function StreamTile({ stream, onRemove, onEdit }) {
  const [status, setStatus] = useState('stopped'); // stopped, connecting, playing, error
  const [errorMessage, setErrorMessage] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [frameBuffer, setFrameBuffer] = useState([]);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showThumbnail, setShowThumbnail] = useState(true);
  
  const canvasRef = useRef(null);
  const playerRef = useRef(null);
  const wsRef = useRef(null);
  const isRewindingRef = useRef(false);
  const originalWriteRef = useRef(null);
  const lastFrameTimeRef = useRef(0);
  const clientIdRef = useRef(config.generateClientId());

  const connectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const wsUrl = stream.ws_url || config.WS_ENDPOINTS.STREAM(stream.id, false, clientIdRef.current);
    console.log('Connecting to WebSocket:', wsUrl);
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected for stream:', stream.id);
      setStatus('connected');
      // Send start command
      ws.send(JSON.stringify({ action: 'start' }));
    };

    ws.onmessage = (event) => {
      console.log('WebSocket message received:', typeof event.data, event.data.length || 'N/A');
      if (typeof event.data === 'string') {
        // Handle JSON messages (status updates, errors)
        try {
          const data = JSON.parse(event.data);
          console.log('Parsed JSON message:', data);
          handleJsonMessage(data);
        } catch (error) {
          console.error('Error parsing JSON message:', error);
        }
      } else {
        // Handle binary data (video stream) - this should not happen for control connections
        console.log('Received binary data on control connection - this should not happen');
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatus('error');
      setErrorMessage('WebSocket connection failed');
    };

    ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
      if (status !== 'stopped') {
        setStatus('error');
        setErrorMessage('Connection closed unexpectedly');
      }
      cleanupPlayer();
    };
  };

  const handleJsonMessage = (data) => {
    switch (data.type) {
      case 'status':
        setStatus(data.phase);
        if (data.phase === 'playing') {
          setIsPlaying(true);
          // Don't initialize JSMpeg here - wait for video_start signal
        } else if (data.phase === 'stopped') {
          setIsPlaying(false);
          cleanupPlayer();
        }
        break;
      case 'video_start':
        // Video is about to start, initialize JSMpeg now
        console.log('Video start signal received');
        initializeJSMpeg();
        break;
      case 'error':
        setStatus('error');
        setErrorMessage(data.message || 'Unknown error');
        cleanupPlayer();
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const initializeJSMpeg = () => {
    console.log('initializeJSMpeg called');
    if (playerRef.current) {
      // Player already exists, don't reinitialize
      console.log('JSMpeg player already exists');
      return;
    }

    if (!canvasRef.current) {
      console.error('Canvas not available');
      return;
    }

    try {
      const JSMpeg = window.JSMpeg;
      console.log('JSMpeg library available:', !!JSMpeg);
      if (!JSMpeg) {
        console.error('JSMpeg not available, will retry in 1 second');
        // Retry after 1 second in case the library is still loading
        setTimeout(() => {
          if (isPlaying) { // Only retry if still playing
            initializeJSMpeg();
          }
        }, 1000);
        return;
      }

      // Create a separate WebSocket URL for JSMpeg with video_only=true
      const wsUrl = config.WS_ENDPOINTS.STREAM(stream.id, true, clientIdRef.current);
      
      console.log('Initializing JSMpeg with URL:', wsUrl);
      console.log('Canvas element:', canvasRef.current);
      
      playerRef.current = new JSMpeg.Player(wsUrl, {
        canvas: canvasRef.current,
        autoplay: true,
        audio: false,
        loop: false,
        onPlay: () => {
          console.log('JSMpeg player started');
          setStatus('playing');
          setIsPlaying(true);
        },
        onError: (error) => {
          console.error('JSMpeg player error:', error);
          setStatus('error');
          setErrorMessage('Video player error');
        },
        onEnded: () => {
          console.log('JSMpeg player ended');
          setStatus('stopped');
          setIsPlaying(false);
        },
        onConnect: () => {
          console.log('JSMpeg WebSocket connected');
        },
        onDisconnect: () => {
          console.log('JSMpeg WebSocket disconnected');
        },
        onSourceEstablished: () => {
          console.log('JSMpeg source established');
          setFrameBuffer([]);
        },
        onSourceCompleted: () => {
          console.log('JSMpeg source completed');
        },
        onDecode: (decoder, time) => {
          // Store frame every 2 seconds for rewind buffer
          if (time - lastFrameTimeRef.current >= 2.0) {
            lastFrameTimeRef.current = time;
            
            canvasRef.current.toBlob((blob) => {
              if (blob) {
                const frameData = {
                  time: time,
                  timestamp: Date.now(),
                  canvasData: URL.createObjectURL(blob)
                };
                
                setFrameBuffer(prev => {
                  const newBuffer = [...prev, frameData];
                  // Keep only last 15 frames (30 seconds at 2fps)
                  if (newBuffer.length > 15) {
                    // Clean up old frame
                    const oldFrame = newBuffer.shift();
                    if (oldFrame.canvasData) {
                      URL.revokeObjectURL(oldFrame.canvasData);
                    }
                  }
                  return newBuffer;
                });
              }
            }, 'image/jpeg', 0.7);
          }
        },
        onPlay: () => {
          console.log('JSMpeg player started');
          setStatus('playing');
          setIsPlaying(true);
          setShowThumbnail(false); // Hide thumbnail when video starts playing
        },
        onPause: () => {
          console.log('JSMpeg player paused');
        },
        onStalled: () => {
          console.log('JSMpeg player stalled');
        }
      });
      
      console.log('JSMpeg player created:', playerRef.current);
      
    } catch (error) {
      console.error('Error initializing JSMpeg player:', error);
      setStatus('error');
      setErrorMessage('Failed to initialize video player');
    }
  };

  const cleanupPlayer = () => {
    if (playerRef.current) {
      try {
        playerRef.current.destroy();
      } catch (error) {
        console.error('Error destroying player:', error);
      }
      playerRef.current = null;
    }
    
    // Reset all refs
    originalWriteRef.current = null;
    isRewindingRef.current = false;
    setIsPlaying(false);
    
    // Clean up frame buffer
    frameBuffer.forEach(frame => {
      if (frame.canvasData) {
        URL.revokeObjectURL(frame.canvasData);
      }
    });
    
    // Reset frame buffer
    setFrameBuffer([]);
  };

  const handlePlay = () => {
    setStatus('connecting');
    setErrorMessage('');
    setShowThumbnail(false); // Hide thumbnail when starting video
    cleanupPlayer(); // Clean up any existing player
    connectWebSocket();
  };

  const handleStop = () => {
    setStatus('stopped');
    setErrorMessage('');
    setShowThumbnail(true); // Show thumbnail when stopping video
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({ action: 'stop' }));
      wsRef.current.close();
    }
    cleanupPlayer();
  };

  const handleReconnect = () => {
    handleStop();
    setTimeout(() => {
      handlePlay();
    }, 1000);
  };

  const muteJSMpegIngest = () => {
    const player = playerRef.current;
    if (!player) return;
    if (!originalWriteRef.current) {
      originalWriteRef.current = player.write;     // backup
      player.write = () => {};                     // drop incoming chunks
    }
    // (optional) also disable renderer updates while paused
    if (player.renderer) player.renderer.enabled = false;
  };

  const unmuteJSMpegIngest = () => {
    const player = playerRef.current;
    if (!player) return;
    if (originalWriteRef.current) {
      player.write = originalWriteRef.current;     // restore
      originalWriteRef.current = null;
    }
    if (player.renderer) player.renderer.enabled = true;

    // Try to clear any residual buffered data if JSMpeg exposes it
    try {
      if (player.demuxer && player.demuxer.reset) player.demuxer.reset();
      if (player.video && player.video.buffer && player.video.buffer.reset) {
        player.video.buffer.reset();
      }
    } catch (_) {}
  };

  const handlePauseResume = () => {
    const player = playerRef.current;
    if (!player) return;

    if (isPaused) {
      // Resume
      unmuteJSMpegIngest();
      isRewindingRef.current = false;
      setIsPaused(false);
      player.play();
      console.log('Resumed');
    } else {
      // Pause: freeze the current frame and stop ingest
      setIsPaused(true);
      isRewindingRef.current = true;
      muteJSMpegIngest();
      player.pause(); // stop JSMpeg loop; socket remains open
      console.log('Paused');
    }
  };



  const handleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const handleRemove = () => {
    handleStop();
    onRemove(stream.id);
  };

  const handleEdit = () => {
    setShowEditModal(true);
  };

  const handleEditClose = () => {
    setShowEditModal(false);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      cleanupPlayer();
    };
  }, []);

  // Check for JSMpeg library availability
  useEffect(() => {
    const checkJSMpeg = () => {
      if (window.JSMpeg) {
        console.log('JSMpeg library is available');
      } else {
        console.log('JSMpeg library not yet available');
        // Check again in 500ms
        setTimeout(checkJSMpeg, 500);
      }
    };
    
    checkJSMpeg();
  }, []);

  const getStatusText = () => {
    switch (status) {
      case 'connecting':
        return 'Connecting...';
      case 'playing':
        return 'Playing';
      case 'error':
        return 'Error';
      case 'stopped':
        return 'Stopped';
      default:
        return 'Unknown';
    }
  };

  const getStatusClass = () => {
    return `stream-status ${status}`;
  };

  return (
    <>
      {isExpanded && (
        <div className="expand-backdrop" onClick={handleExpand}></div>
      )}
      <div className={`stream-tile ${isExpanded ? 'expanded' : ''}`}>
      <div className="stream-header">
        <div className="stream-title">
          {stream.label || 'Unnamed Stream'}
        </div>
        <div className="stream-controls">
          {status === 'error' && (
            <button
              className="control-button"
              onClick={handleReconnect}
            >
              Retry
            </button>
          )}
          
          <button
            className="control-button"
            onClick={handleEdit}
            title="Edit Stream"
          >
            ✏️ Edit
          </button>
          
          <button
            className="control-button danger"
            onClick={handleRemove}
          >
            Remove
          </button>
        </div>
      </div>
      
      <div 
        className="stream-video-container"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Show thumbnail when not playing */}
        {showThumbnail && (
          <StreamThumbnail
            streamId={stream.id}
            streamUrl={stream.url}
            className="stream-thumbnail-container"
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              zIndex: 1
            }}
            onLoad={(data) => {
              console.log('Thumbnail loaded for stream:', stream.id);
            }}
            onError={(error) => {
              console.error('Thumbnail error for stream:', stream.id, error);
            }}
          />
        )}
        
        <canvas
          ref={canvasRef}
          className="stream-video"
          style={{
            display: showThumbnail ? 'none' : 'block'
          }}
        />
        
        <div className={getStatusClass()}>
          {getStatusText()}
        </div>
        
        {/* Expand button */}
        <button
          className="expand-button"
          onClick={handleExpand}
          title={isExpanded ? "Collapse" : "Expand"}
        >
          {isExpanded ? '✕' : '⤢'}
        </button>
        
        {status === 'connecting' && (
          <div className="stream-overlay">
            <div className="loading-spinner"></div>
          </div>
        )}
        
        {status === 'error' && (
          <div className="stream-overlay">
            <div>
              <div style={{ marginBottom: '1rem' }}>⚠️ {errorMessage}</div>
              <button
                className="control-button"
                onClick={handleReconnect}
              >
                Retry Connection
              </button>
            </div>
          </div>
        )}
        
        {status === 'stopped' && (
          <div className="stream-overlay" style={{ zIndex: 10 }}>
            <button
              className="control-button play-button"
              onClick={handlePlay}
              disabled={status === 'connecting'}
            >
              ▶ Play
            </button>
          </div>
        )}
        
        {/* Pause/Resume button overlay */}
        {isPlaying && isHovered && (
          <div className="stream-control-overlay">
            <button
              className="control-button pause-resume-btn"
              onClick={handlePauseResume}
            >
              {isPaused ? '▶' : '⏸'}
            </button>
          </div>
        )}
        

      </div>
    </div>
    
    {showEditModal && (
      <EditStreamModal
        stream={stream}
        onEdit={onEdit}
        onClose={handleEditClose}
        loading={status === 'connecting'}
      />
    )}
    </>
  );
}

export default StreamTile;
