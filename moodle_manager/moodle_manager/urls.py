from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='moodle/')),
    path('admin/', admin.site.urls),
    path('moodle/', include('moodle_management.urls')),  # UI views
    path('api/', include('moodle_management.urls_api')),  # API views
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]