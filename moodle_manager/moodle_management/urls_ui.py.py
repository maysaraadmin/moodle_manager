from django.urls import path
from .views import (
    MoodlePlatformListView, MoodlePlatformCreateView,
    MoodlePlatformUpdateView, MoodlePlatformDetailView,
    MoodlePlatformDeleteView, test_connection
)

urlpatterns = [
    path('', MoodlePlatformListView.as_view(), name='platform-list'),
    path('add/', MoodlePlatformCreateView.as_view(), name='platform-add'),
    path('<int:pk>/', MoodlePlatformDetailView.as_view(), name='platform-detail'),
    path('<int:pk>/edit/', MoodlePlatformUpdateView.as_view(), name='platform-edit'),
    path('<int:pk>/delete/', MoodlePlatformDeleteView.as_view(), name='platform-delete'),
    path('<int:pk>/test/', test_connection, name='platform-test'),
]