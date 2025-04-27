from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from moodle_management.views import (
    MoodlePlatformViewSet,
    MoodleUserViewSet,
    UserPlatformAssociationViewSet,
    api_root
)

router = DefaultRouter()
router.register(r'platforms', MoodlePlatformViewSet, basename='moodleplatform')
router.register(r'users', MoodleUserViewSet, basename='moodleuser')
router.register(r'associations', UserPlatformAssociationViewSet, basename='userplatformassociation')

urlpatterns = [
    path('', RedirectView.as_view(url='moodle/')),
    path('admin/', admin.site.urls),
    path('moodle/', include('moodle_management.urls')),  # UI views
    path('api/', include('moodle_management.urls_api')),  # API views
    path('api-auth/', include('rest_framework.urls')),
]
