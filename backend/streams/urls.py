from django.urls import path
from .views import (
    StreamListCreateView, 
    StreamDetailView, 
    health_check,
    stream_thumbnail,
    refresh_thumbnail,
    thumbnail_cache_stats
)

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('streams/', StreamListCreateView.as_view(), name='stream-list-create'),
    path('streams/<uuid:id>/', StreamDetailView.as_view(), name='stream-detail'),
    path('streams/<uuid:stream_id>/thumbnail/', stream_thumbnail, name='stream-thumbnail'),
    path('streams/<uuid:stream_id>/thumbnail/refresh/', refresh_thumbnail, name='refresh-thumbnail'),
    path('thumbnails/cache/stats/', thumbnail_cache_stats, name='thumbnail-cache-stats'),
]
