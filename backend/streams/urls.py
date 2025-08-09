from django.urls import path
from .views import StreamListCreateView, StreamDetailView, health_check

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('streams/', StreamListCreateView.as_view(), name='stream-list-create'),
    path('streams/<uuid:id>/', StreamDetailView.as_view(), name='stream-detail'),
]
