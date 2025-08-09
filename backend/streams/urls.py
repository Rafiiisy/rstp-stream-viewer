from django.urls import path
from .views import StreamListCreateView, StreamDetailView, health_check, test_view

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('test/', test_view, name='test'),
    path('streams/', StreamListCreateView.as_view(), name='stream-list-create'),
    path('streams/<uuid:id>/', StreamDetailView.as_view(), name='stream-detail'),
]
