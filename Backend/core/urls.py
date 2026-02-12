"""
URL Configuration for the core app API endpoints.
With AppContent and JournalSettings.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter()
router.register(r'news', views.NewsViewSet, basename='news')
router.register(r'gallery', views.GalleryItemViewSet, basename='gallery')
router.register(r'listeners', views.ListenerViewSet, basename='listeners')
router.register(r'teachers', views.TeacherViewSet, basename='teachers')
router.register(r'personnel', views.PersonnelViewSet, basename='personnel')
router.register(r'courses', views.CourseViewSet, basename='courses')
router.register(r'journal', views.JournalIssueViewSet, basename='journal')
router.register(r'documents', views.DocumentViewSet, basename='documents')
router.register(r'statistics', views.StatisticsViewSet, basename='statistics')
router.register(r'yearly-statistics', views.YearlyStatisticsViewSet, basename='yearly-statistics')
router.register(r'content', views.AppContentViewSet, basename='content')
router.register(r'journal-settings', views.JournalSettingsViewSet, basename='journal-settings')
router.register(r'international-content', views.InternationalRelationViewSet, basename='international-content')
router.register(r'foreign-partners', views.ForeignPartnerViewSet, basename='foreign-partners')
router.register(r'collaboration-projects', views.CollaborationProjectViewSet, basename='collaboration-projects')
router.register(r'art-gallery', views.ArtGalleryItemViewSet, basename='art-gallery')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # All data endpoint (for initial load)
    path('all-data/', views.get_all_data, name='all-data'),

    # Authentication endpoints
    path('login/', views.custom_login, name='custom-login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Legacy pdPlans endpoint (alias for listeners)
    path('pdplans/', views.ListenerViewSet.as_view({'get': 'list', 'post': 'create'}), name='pdplans-list'),
    path('pdplans/<int:pk>/', views.ListenerViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='pdplans-detail'),
    path('pdplans/search/', views.ListenerViewSet.as_view({'get': 'search'}), name='pdplans-search'),
    path('pdplans/bulk-import/', views.ListenerViewSet.as_view({'post': 'bulk_import'}), name='pdplans-bulk-import'),
]
