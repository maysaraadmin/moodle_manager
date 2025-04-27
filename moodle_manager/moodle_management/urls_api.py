from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
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
    path('', api_root, name='api-root'),
] + router.urls