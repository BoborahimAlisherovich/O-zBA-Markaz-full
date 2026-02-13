"""
URL configuration for markaz_backend project.
"""
from django.views.generic import TemplateView
from django.urls import re_path

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    re_path(r'^.*$', TemplateView.as_view(template_name="index.html")),

]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
