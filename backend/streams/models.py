import uuid
from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from urllib.parse import urlparse

def validate_rtsp_url(value):
    """Validate that the URL is a valid RTSP URL"""
    if not value.startswith('rtsp://'):
        raise ValidationError('URL must be a valid RTSP URL starting with rtsp://')
    
    # Parse the URL to check if it's well-formed
    try:
        parsed = urlparse(value)
        if not parsed.netloc:
            raise ValidationError('Invalid RTSP URL format')
    except Exception:
        raise ValidationError('Invalid RTSP URL format')

class Stream(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.CharField(max_length=500, validators=[validate_rtsp_url])
    label = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.label or 'Unnamed Stream'} ({self.url})"

    @property
    def ws_url(self):
        """Generate WebSocket URL for this stream"""
        import os
        # Use the PORT environment variable that Railway provides
        port = os.environ.get('PORT', '8000')
        # Use the actual domain instead of localhost for production
        host = os.environ.get('RAILWAY_STATIC_URL', 'localhost')
        protocol = 'wss' if host != 'localhost' else 'ws'
        return f"{protocol}://{host}/ws/stream?id={self.id}"
