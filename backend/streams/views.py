from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from django.shortcuts import get_object_or_404
from .models import Stream
from .serializers import StreamSerializer, StreamCreateSerializer
from .thumbnail_service import thumbnail_service
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
    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def stream_thumbnail(request, stream_id):
    """Get thumbnail for a specific stream"""
    try:
        stream = get_object_or_404(Stream, id=stream_id, is_active=True)
        force_refresh = request.GET.get('refresh', 'false').lower() == 'true'
        
        thumbnail_data = thumbnail_service.get_thumbnail(
            str(stream.id), 
            stream.url, 
            force_refresh=force_refresh
        )
        
        if thumbnail_data:
            return Response(thumbnail_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Failed to generate thumbnail'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Stream.DoesNotExist:
        return Response(
            {'error': 'Stream not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def refresh_thumbnail(request, stream_id):
    """Force refresh thumbnail for a specific stream"""
    try:
        stream = get_object_or_404(Stream, id=stream_id, is_active=True)
        
        # Clear cache for this stream
        thumbnail_service.clear_cache(str(stream.id))
        
        return Response(
            {'message': 'Thumbnail cache cleared, next request will generate new thumbnail'}, 
            status=status.HTTP_200_OK
        )
            
    except Stream.DoesNotExist:
        return Response(
            {'error': 'Stream not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def thumbnail_cache_stats(request):
    """Get thumbnail cache statistics"""
    try:
        stats = thumbnail_service.get_cache_stats()
        return Response(stats, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
