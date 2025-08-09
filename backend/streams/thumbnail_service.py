import asyncio
import base64
import logging
import os
import tempfile
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import subprocess

logger = logging.getLogger(__name__)

class ThumbnailService:
    def __init__(self):
        self.thumbnail_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 300  # 5 minutes
        self.thumbnail_quality = 85
        self.thumbnail_width = 320
        self.thumbnail_height = 240
        self.ffmpeg_timeout = 10  # seconds
        
    def get_thumbnail(self, stream_id: str, rtsp_url: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """Get thumbnail for a stream, either from cache or generate new one"""
        cache_key = f"{stream_id}_{self._hash_url(rtsp_url)}"
        
        # Check cache first
        if not force_refresh and cache_key in self.thumbnail_cache:
            cached = self.thumbnail_cache[cache_key]
            if self._is_cache_valid(cached):
                logger.info(f"Returning cached thumbnail for stream {stream_id}")
                return cached
        
        # Generate new thumbnail
        logger.info(f"Generating thumbnail for stream {stream_id}")
        thumbnail_data = self._generate_thumbnail(rtsp_url)
        
        if thumbnail_data:
            thumbnail_info = {
                'thumbnail': thumbnail_data,
                'timestamp': datetime.utcnow().isoformat(),
                'size': {'width': self.thumbnail_width, 'height': self.thumbnail_height},
                'format': 'jpeg',
                'quality': self.thumbnail_quality,
                'stream_id': stream_id
            }
            
            # Cache the thumbnail
            self.thumbnail_cache[cache_key] = thumbnail_info
            logger.info(f"Thumbnail generated and cached for stream {stream_id}")
            return thumbnail_info
        else:
            logger.error(f"Failed to generate thumbnail for stream {stream_id}")
            return None
    
    def _generate_thumbnail(self, rtsp_url: str) -> Optional[str]:
        """Generate thumbnail from RTSP stream using FFmpeg"""
        try:
            # Create temporary file for thumbnail
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # FFmpeg command to capture single frame
            cmd = [
                'ffmpeg',
                '-rtsp_transport', 'tcp',
                '-i', rtsp_url,
                '-vframes', '1',
                '-vf', f'scale={self.thumbnail_width}:{self.thumbnail_height}',
                '-q:v', '2',  # High quality
                '-f', 'image2',
                '-y',  # Overwrite output file
                temp_path
            ]
            
            logger.debug(f"Running FFmpeg command: {' '.join(cmd)}")
            
            # Run FFmpeg with timeout using subprocess
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.ffmpeg_timeout
            )
            
            if process.returncode == 0 and os.path.exists(temp_path):
                # Read the generated thumbnail
                with open(temp_path, 'rb') as f:
                    image_data = f.read()
                
                # Convert to base64
                base64_data = base64.b64encode(image_data).decode('utf-8')
                data_url = f"data:image/jpeg;base64,{base64_data}"
                
                logger.debug(f"Thumbnail generated successfully, size: {len(image_data)} bytes")
                return data_url
            else:
                logger.error(f"FFmpeg failed with return code {process.returncode}")
                if process.stderr:
                    logger.error(f"FFmpeg stderr: {process.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"FFmpeg thumbnail generation timed out after {self.ffmpeg_timeout} seconds")
            return None
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            return None
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_path}: {e}")
    
    def _hash_url(self, url: str) -> str:
        """Create a simple hash of the URL for cache key"""
        return str(hash(url))
    
    def _is_cache_valid(self, cached_data: Dict[str, Any]) -> bool:
        """Check if cached thumbnail is still valid"""
        try:
            timestamp_str = cached_data.get('timestamp')
            if not timestamp_str:
                return False
            
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            age = datetime.utcnow() - timestamp.replace(tzinfo=None)
            
            return age.total_seconds() < self.cache_ttl
        except Exception as e:
            logger.warning(f"Error checking cache validity: {e}")
            return False
    
    def clear_cache(self, stream_id: Optional[str] = None):
        """Clear thumbnail cache"""
        if stream_id:
            # Clear specific stream cache
            keys_to_remove = [k for k in self.thumbnail_cache.keys() if k.startswith(f"{stream_id}_")]
            for key in keys_to_remove:
                del self.thumbnail_cache[key]
            logger.info(f"Cleared cache for stream {stream_id}")
        else:
            # Clear all cache
            self.thumbnail_cache.clear()
            logger.info("Cleared all thumbnail cache")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'total_cached': len(self.thumbnail_cache),
            'cache_ttl': self.cache_ttl,
            'cached_streams': list(set(item.get('stream_id') for item in self.thumbnail_cache.values()))
        }

# Global thumbnail service instance
thumbnail_service = ThumbnailService()
