import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404
from .models import Stream
from .ffmpeg_helper import FFmpegProcess
from django.conf import settings

logger = logging.getLogger(__name__)

# Global stream manager to share FFmpeg processes between connections
class StreamManager:
    def __init__(self):
        self.streams = {}  # stream_id -> StreamInfo
        self.lock = asyncio.Lock()
    
    async def get_or_create_stream(self, stream_id, rtsp_url):
        async with self.lock:
            if stream_id not in self.streams:
                self.streams[stream_id] = StreamInfo(stream_id, rtsp_url)
            return self.streams[stream_id]
    
    async def remove_stream(self, stream_id):
        async with self.lock:
            if stream_id in self.streams:
                await self.streams[stream_id].stop()
                del self.streams[stream_id]

class StreamInfo:
    def __init__(self, stream_id, rtsp_url):
        self.stream_id = stream_id
        self.rtsp_url = rtsp_url
        self.ffmpeg_process = None
        self.is_playing = False
        self.connections = set()  # Set of WebSocket connections
        self.video_buffer = asyncio.Queue(maxsize=100)  # Buffer for video chunks
    
    async def add_connection(self, connection):
        self.connections.add(connection)
        logger.info(f"Added connection to stream {self.stream_id} - total connections: {len(self.connections)}")
        if not self.is_playing:
            logger.info(f"Starting stream for {self.stream_id} - no connections were playing")
            await self.start()
    
    async def remove_connection(self, connection):
        self.connections.discard(connection)
        logger.info(f"Removed connection from stream {self.stream_id} - total connections: {len(self.connections)}")
        if not self.connections and self.is_playing:
            logger.info(f"Stopping stream for {self.stream_id} - no more connections")
            await self.stop()
    
    async def start(self):
        if self.is_playing:
            logger.info(f"Stream {self.stream_id} already playing")
            return True
        
        try:
            logger.info(f"Starting FFmpeg for stream {self.stream_id}")
            self.ffmpeg_process = FFmpegProcess(self.rtsp_url)
            success = await self.ffmpeg_process.start()
            
            if success:
                self.is_playing = True
                logger.info(f"FFmpeg started successfully for stream {self.stream_id}")
                asyncio.create_task(self._stream_video_data())
                logger.info(f"Started shared stream for: {self._mask_url(self.rtsp_url)}")
                return True
            else:
                logger.error(f"Failed to start FFmpeg for stream: {self._mask_url(self.rtsp_url)}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting stream: {e}")
            return False
    
    async def stop(self):
        if self.ffmpeg_process:
            await self.ffmpeg_process.stop()
            self.ffmpeg_process = None
        self.is_playing = False
        logger.info(f"Stopped shared stream for: {self._mask_url(self.rtsp_url)}")
    
    async def _stream_video_data(self):
        """Stream video data to all connected WebSockets"""
        logger.info(f"Starting video streaming for stream {self.stream_id}")
        try:
            chunk_count = 0
            while self.is_playing and self.ffmpeg_process and self.ffmpeg_process.is_alive():
                chunk = await self.ffmpeg_process.read_output()
                
                if chunk is None:
                    logger.info(f"FFmpeg process ended for stream {self.stream_id}")
                    break
                
                chunk_count += 1
                if chunk_count % 100 == 0:  # Log every 100 chunks
                    logger.info(f"Stream {self.stream_id}: sent {chunk_count} chunks, chunk size: {len(chunk)} bytes")
                
                # Log first few chunks for debugging
                if chunk_count <= 5:
                    logger.info(f"Stream {self.stream_id}: chunk {chunk_count}, size: {len(chunk)} bytes, first 16 bytes: {chunk[:16].hex()}")
                
                # Send to all video-only connections
                video_connections = [conn for conn in self.connections if conn.video_only]
                control_connections = [conn for conn in self.connections if not conn.video_only]
                
                logger.debug(f"Stream {self.stream_id}: {len(video_connections)} video connections, {len(control_connections)} control connections")
                
                if video_connections:
                    logger.debug(f"Sending chunk to {len(video_connections)} video connections, chunk size: {len(chunk)} bytes")
                    for connection in video_connections:
                        try:
                            await connection.send(bytes_data=chunk)
                        except Exception as e:
                            logger.error(f"Error sending video to connection: {e}")
                            await self.remove_connection(connection)
                else:
                    logger.debug(f"No video connections to send chunk to")
                
                await asyncio.sleep(0.01)
            
            # Stream ended
            if self.is_playing:
                self.is_playing = False
                logger.info(f"Stream {self.stream_id} ended - total chunks sent: {chunk_count}")
                # Notify control connections
                control_connections = [conn for conn in self.connections if not conn.video_only]
                for connection in control_connections:
                    try:
                        await connection.send(text_data=json.dumps({
                            'type': 'error',
                            'code': 'FFMPEG_EXIT',
                            'message': 'Stream ended unexpectedly'
                        }))
                    except Exception as e:
                        logger.error(f"Error notifying control connection: {e}")
                        await self.remove_connection(connection)
                
        except Exception as e:
            logger.error(f"Error streaming video data: {e}")

    async def send_video_data(self, data):
        """Send video data to this connection (only for video-only connections)"""
        if self.video_only:
            await super().send(bytes_data=data)

    async def send_control_data(self, data):
        """Send control data to this connection (only for control connections)"""
        if not self.video_only:
            await super().send(text_data=data)
    
    def _mask_url(self, url):
        """Mask credentials in URL for logging"""
        if not url:
            return url
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if parsed.username and parsed.password:
                masked_netloc = f"{parsed.username}:***@{parsed.hostname}"
                if parsed.port:
                    masked_netloc += f":{parsed.port}"
                return f"{parsed.scheme}://{masked_netloc}{parsed.path}"
        except:
            pass
        
        return url

# Global stream manager instance
stream_manager = StreamManager()

class StreamConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream_id = None
        self.rtsp_url = None
        self.video_only = False
        self.stream_info = None

    async def connect(self):
        """Handle WebSocket connection"""
        try:
            # Get stream ID or URL from query parameters
            query_string = self.scope.get('query_string', b'').decode('utf-8')
            params = dict(item.split('=') for item in query_string.split('&') if '=' in item)
            
            self.stream_id = params.get('id')
            self.rtsp_url = params.get('url')
            self.video_only = params.get('video_only', 'false').lower() == 'true'
            
            logger.info(f"WebSocket connection attempt - stream_id: {self.stream_id}, video_only: {self.video_only}")
            
            if not self.stream_id and not self.rtsp_url:
                await self.close(code=4000, reason="Missing stream ID or URL")
                return
            
            # If stream_id provided, get the stream from database
            if self.stream_id:
                stream = await self._get_stream(self.stream_id)
                if not stream:
                    await self.close(code=4004, reason="Stream not found")
                    return
                self.rtsp_url = stream.url
            
            # Validate RTSP URL
            if not self.rtsp_url.startswith('rtsp://'):
                await self.close(code=4000, reason="Invalid RTSP URL")
                return
            
            # Accept the connection
            await self.accept()
            
            # Get or create shared stream info
            self.stream_info = await stream_manager.get_or_create_stream(self.stream_id or 'direct', self.rtsp_url)
            await self.stream_info.add_connection(self)
            
            logger.info(f"Connection added to stream manager - total connections: {len(self.stream_info.connections)}")
            
            if self.video_only:
                # For JSMpeg connections, start streaming immediately
                logger.info(f"JSMpeg WebSocket connected for stream: {self._mask_url(self.rtsp_url)}")
                # The stream will be started automatically by the shared manager
            else:
                # For control connections, send initial status
                await self.send(text_data=json.dumps({
                    'type': 'status',
                    'phase': 'connected'
                }))
                logger.info(f"Control WebSocket connected for stream: {self._mask_url(self.rtsp_url)}")
            
        except Exception as e:
            logger.error(f"Error in WebSocket connect: {e}")
            await self.close(code=1011, reason="Internal server error")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            if self.stream_info:
                await self.stream_info.remove_connection(self)
            
            logger.info(f"WebSocket disconnected for stream: {self._mask_url(self.rtsp_url) if self.rtsp_url else 'unknown'}")
            
        except Exception as e:
            logger.error(f"Error in WebSocket disconnect: {e}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        # Skip message handling for video-only connections
        if self.video_only:
            return
            
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'start':
                await self._start_stream()
            elif action == 'stop':
                await self._stop_stream()
            elif action == 'reconnect':
                await self._reconnect_stream()
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'code': 'INVALID_ACTION',
                    'message': f'Unknown action: {action}'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'code': 'INVALID_JSON',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error'
            }))

    async def _start_stream(self):
        """Start the RTSP stream"""
        if not self.stream_info:
            return
        
        try:
            # Send connecting status
            await self.send(text_data=json.dumps({
                'type': 'status',
                'phase': 'connecting'
            }))
            
            # Start the shared stream
            success = await self.stream_info.start()
            
            if not success:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'code': 'FFMPEG_START_FAILED',
                    'message': 'Failed to start video stream'
                }))
                return
            
            # Send playing status
            await self.send(text_data=json.dumps({
                'type': 'status',
                'phase': 'playing'
            }))
            
            # Send video start signal
            await self.send(text_data=json.dumps({
                'type': 'video_start'
            }))
            
        except Exception as e:
            logger.error(f"Error starting stream: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'code': 'START_FAILED',
                'message': 'Failed to start stream'
            }))

    async def _stop_stream(self):
        """Stop the RTSP stream"""
        try:
            if self.stream_info:
                await self.stream_info.stop()
            
            await self.send(text_data=json.dumps({
                'type': 'status',
                'phase': 'stopped'
            }))
            
        except Exception as e:
            logger.error(f"Error stopping stream: {e}")

    async def _reconnect_stream(self):
        """Reconnect the stream"""
        await self._stop_stream()
        await asyncio.sleep(1)  # Brief pause
        await self._start_stream()

    @database_sync_to_async
    def _get_stream(self, stream_id):
        """Get stream from database"""
        try:
            return Stream.objects.get(id=stream_id, is_active=True)
        except Stream.DoesNotExist:
            return None

    def _mask_url(self, url):
        """Mask credentials in URL for logging"""
        if not url:
            return url
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if parsed.username and parsed.password:
                masked_netloc = f"{parsed.username}:***@{parsed.hostname}"
                if parsed.port:
                    masked_netloc += f":{parsed.port}"
                return f"{parsed.scheme}://{masked_netloc}{parsed.path}"
        except:
            pass
        
        return url
