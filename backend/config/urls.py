from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def root_view(request):
    return JsonResponse({
        'message': 'RTSP Stream Viewer API',
        'status': 'running',
        'endpoints': {
            'health': '/api/health/',
            'streams': '/api/streams/',
            'admin': '/admin/'
        }
    })

urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('api/', include('streams.urls')),
]
