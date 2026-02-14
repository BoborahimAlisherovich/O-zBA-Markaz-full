"""URL configuration for markaz_backend project."""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('journal/', views.journal, name='journal'),
    path('international/', views.international, name='international'),
    path('students/', views.students, name='students'),
    path('open-data/', views.open_data, name='open_data'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
