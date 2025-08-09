from django.contrib import admin
from .models import Stream

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'url', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['label', 'url']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')
