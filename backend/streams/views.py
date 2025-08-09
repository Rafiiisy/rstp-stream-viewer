from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Stream
from .serializers import StreamSerializer, StreamCreateSerializer
import subprocess
import re

class BaseStreamView:
    def _validate_rtsp_url(self, url):
        """Basic validation of RTSP URL using ffprobe"""
        try:
            # Use ffprobe to check if the stream is accessible
            cmd = [
                'ffprobe', 
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                '-rtsp_transport', 'tcp',
                url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            # If ffprobe is not available, just validate URL format
            return url.startswith('rtsp://')

class StreamListCreateView(BaseStreamView, ListCreateAPIView):
    queryset = Stream.objects.filter(is_active=True)
    serializer_class = StreamSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StreamCreateSerializer
        return StreamSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Validate RTSP URL with ffprobe
            url = serializer.validated_data['url']
            if not self._validate_rtsp_url(url):
                return Response(
                    {'error': 'Invalid RTSP URL or stream not accessible'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            stream = serializer.save()
            response_serializer = StreamSerializer(stream)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StreamDetailView(BaseStreamView, RetrieveDestroyAPIView):
    queryset = Stream.objects.filter(is_active=True)
    serializer_class = StreamSerializer
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return StreamCreateSerializer
        return StreamSerializer

    def put(self, request, *args, **kwargs):
        """Handle PUT requests for updating streams"""
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=False)
        if serializer.is_valid():
            # Validate RTSP URL with ffprobe
            url = serializer.validated_data.get('url')
            if url and not self._validate_rtsp_url(url):
                return Response(
                    {'error': 'Invalid RTSP URL or stream not accessible'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            stream = serializer.save()
            response_serializer = StreamSerializer(stream)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        """Handle PATCH requests for partial updates"""
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        if serializer.is_valid():
            # Validate RTSP URL with ffprobe
            url = serializer.validated_data.get('url')
            if url and not self._validate_rtsp_url(url):
                return Response(
                    {'error': 'Invalid RTSP URL or stream not accessible'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            stream = serializer.save()
            response_serializer = StreamSerializer(stream)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        stream = self.get_object()
        stream.is_active = False
        stream.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    try:
        # Try to access the database
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return Response({
        'status': 'healthy',
        'database': db_status,
        'timestamp': timezone.now().isoformat()
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def test_view(request):
    """Simple test endpoint"""
    return Response({
        'message': 'API is working!',
        'method': request.method,
        'path': request.path,
        'timestamp': timezone.now().isoformat()
    }, status=status.HTTP_200_OK)
