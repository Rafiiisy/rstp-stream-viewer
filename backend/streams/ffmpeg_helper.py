import asyncio
import logging
import subprocess
import sys
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)

class FFmpegProcess:
    def __init__(self, rtsp_url: str, quality: str = 'medium'):
        self.rtsp_url = rtsp_url
        self.quality = quality
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.error_message = None
        
    def _mask_credentials(self, url: str) -> str:
        """Mask credentials in URL for logging"""
        parsed = urlparse(url)
        if parsed.username and parsed.password:
            masked_netloc = f"{parsed.username}:***@{parsed.hostname}"
            if parsed.port:
                masked_netloc += f":{parsed.port}"
            return f"{parsed.scheme}://{masked_netloc}{parsed.path}"
        return url

    def _get_ffmpeg_command(self) -> list:
        TS_FPS = "25"        # tweak as needed
        GOP    = "50"        # ~2x fps

        return [
            "ffmpeg",
            "-nostdin",
            "-loglevel", "error",
            "-rtsp_transport", "tcp",
            "-fflags", "nobuffer",
            "-flags", "low_delay",
            "-probesize", "32",
            "-analyzeduration", "0",

            "-i", self.rtsp_url,

            # OUTPUT: MPEG-TS container with MPEG-1 video for JSMpeg
            "-f", "mpegts",
            "-codec:v", "mpeg1video",
            "-q:v", "6",              # 2(best) … 31(worst). 6 is fine.
            "-r", TS_FPS,             # fps
            "-g", GOP,                # keyframe interval
            "-bf", "0",               # no B-frames
            "-an",                    # no audio
            "-muxdelay", "0",
            "-muxpreload", "0",

            # Optional: fix size (uncomment if you want)
            # "-s", "640x480",

            "pipe:1",                 # stdout
        ]

    def _start_process_sync(self) -> bool:
        """Start the FFmpeg process synchronously"""
        try:
            cmd = self._get_ffmpeg_command()
            
            # Windows-specific subprocess creation
            if sys.platform == 'win32':
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            self.is_running = True
            logger.info(f"FFmpeg process started with PID: {self.process.pid}")
            return True
            
        except Exception as e:
            import traceback
            self.error_message = f"Failed to start FFmpeg: {str(e)}"
            logger.error(self.error_message)
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False

    async def start(self) -> bool:
        """Start the FFmpeg process"""
        if self.is_running:
            return True
            
        try:
            cmd = self._get_ffmpeg_command()
            masked_url = self._mask_credentials(self.rtsp_url)
            logger.info(f"Starting FFmpeg for stream: {masked_url}")
            logger.info(f"FFmpeg command: {' '.join(cmd)}")
            
            # Use asyncio.to_thread to run the synchronous subprocess creation
            result = await asyncio.to_thread(self._start_process_sync)
            return result
            
        except Exception as e:
            import traceback
            self.error_message = f"Failed to start FFmpeg: {str(e)}"
            logger.error(self.error_message)
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False

    def _stop_process_sync(self):
        """Stop the FFmpeg process synchronously"""
        if self.process and self.is_running:
            try:
                self.process.terminate()
                # Wait a bit for graceful shutdown
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
                
                logger.info(f"FFmpeg process {self.process.pid} stopped")
            except Exception as e:
                logger.error(f"Error stopping FFmpeg process: {e}")
            finally:
                self.process = None
                self.is_running = False

    async def stop(self):
        """Stop the FFmpeg process"""
        await asyncio.to_thread(self._stop_process_sync)

    def _read_output_sync(self) -> Optional[bytes]:
        """Read FFmpeg output synchronously"""
        if not self.process or not self.is_running:
            return None
            
        try:
            # Read a chunk of data
            chunk = self.process.stdout.read(4096)
            if chunk:
                return chunk
            else:
                # Process has ended
                self.is_running = False
                return None
        except Exception as e:
            logger.error(f"Error reading FFmpeg output: {e}")
            self.is_running = False
            return None

    async def read_output(self):
        """Read FFmpeg output asynchronously"""
        return await asyncio.to_thread(self._read_output_sync)

    async def get_error_info(self) -> Dict[str, Any]:
        """Get error information from FFmpeg stderr"""
        if not self.process:
            return {}
            
        try:
            stderr_output = await asyncio.to_thread(lambda: self.process.stderr.read())
            stderr_text = stderr_output.decode('utf-8')
            return self._parse_ffmpeg_errors(stderr_text)
        except:
            return {}

    def _parse_ffmpeg_errors(self, stderr_output: str) -> Dict[str, Any]:
        """Parse FFmpeg error messages"""
        errors = {
            'code': 'UNKNOWN',
            'message': 'Unknown error',
            'details': stderr_output
        }
        
        # Common error patterns
        if '401 Unauthorized' in stderr_output:
            errors['code'] = 'AUTH'
            errors['message'] = 'Authentication failed'
        elif '404 Not Found' in stderr_output:
            errors['code'] = 'NOT_FOUND'
            errors['message'] = 'Stream not found'
        elif 'Connection refused' in stderr_output:
            errors['code'] = 'CONNECTION_REFUSED'
            errors['message'] = 'Connection refused'
        elif 'timeout' in stderr_output.lower():
            errors['code'] = 'TIMEOUT'
            errors['message'] = 'Connection timeout'
        elif 'Invalid data found' in stderr_output:
            errors['code'] = 'INVALID_STREAM'
            errors['message'] = 'Invalid stream format'
        
        return errors

    def is_alive(self) -> bool:
        """Check if the process is still running"""
        if not self.process:
            return False
        return self.process.poll() is None

def _validate_rtsp_url_sync(url: str, timeout: int = 10) -> bool:
    """Validate RTSP URL using ffprobe synchronously"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            '-rtsp_transport', 'tcp',
            '-timeout', str(timeout * 1000000),  # Convert to microseconds
            url
        ]
        
        # Windows-specific subprocess creation
        if sys.platform == 'win32':
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout
            )
        
        return result.returncode == 0
        
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.error(f"Error validating RTSP URL {url}: {e}")
        return False

async def validate_rtsp_url(url: str, timeout: int = 10) -> bool:
    """Validate RTSP URL using ffprobe"""
    return await asyncio.to_thread(_validate_rtsp_url_sync, url, timeout)