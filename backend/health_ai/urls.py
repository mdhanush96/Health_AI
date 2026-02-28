"""
URL configuration for health_ai project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/', include('reports.urls')),
    path('api/', include('ml_engine.urls')),
    path('api/', include('recommendations.urls')),
    path('api/', include('emergency.urls')),
    path('api/', include('history.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
