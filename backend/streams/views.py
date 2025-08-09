from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from django.shortcuts import get_object_or_404
from .models import Stream
from .serializers import StreamSerializer, StreamCreateSerializer
import subprocess
import re

class StreamListCreateView(ListCreateAPIView):
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

class StreamDetailView(RetrieveDestroyAPIView):
    queryset = Stream.objects.filter(is_active=True)
    serializer_class = StreamSerializer
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        stream = self.get_object()
        stream.is_active = False
        stream.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)
