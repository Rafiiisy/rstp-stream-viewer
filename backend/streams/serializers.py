from rest_framework import serializers
from .models import Stream

class StreamSerializer(serializers.ModelSerializer):
    ws_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Stream
        fields = ['id', 'url', 'label', 'created_at', 'ws_url']
        read_only_fields = ['id', 'created_at', 'ws_url']

class StreamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = ['url', 'label']
