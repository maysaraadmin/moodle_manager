from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from rest_framework import viewsets, permissions # Import permissions if you use them
# --- Import models and serializers ---
from .models import MoodlePlatform, MoodleUser, UserPlatformAssociation
from .serializers import MoodlePlatformSerializer, MoodleUserSerializer, UserPlatformAssociationSerializer
# --- Imports for api_root if you uncomment it ---
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

# --- Your Class-Based Views for UI ---
# ... (Keep your existing UI views) ...
class MoodlePlatformListView(ListView):
    model = MoodlePlatform
    template_name = 'moodle_management/platform_list.html'
    context_object_name = 'platforms'

class MoodlePlatformCreateView(CreateView):
    model = MoodlePlatform
    template_name = 'moodle_management/platform_form.html'
    fields = ['name', 'url', 'api_key', 'api_endpoint', 'active'] # Added api_endpoint
    success_url = reverse_lazy('moodle_management:platform-list')

class MoodlePlatformUpdateView(UpdateView):
    model = MoodlePlatform
    template_name = 'moodle_management/platform_form.html'
    fields = ['name', 'url', 'api_key', 'api_endpoint', 'active'] # Added api_endpoint
    success_url = reverse_lazy('moodle_management:platform-list')

class MoodlePlatformDetailView(DetailView):
    model = MoodlePlatform
    template_name = 'moodle_management/platform_detail.html'

class MoodlePlatformDeleteView(DeleteView):
    model = MoodlePlatform
    template_name = 'moodle_management/platform_confirm_delete.html'
    success_url = reverse_lazy('moodle_management:platform-list')


# --- Your Function-Based View ---
def test_connection(request, pk):
    # Your test connection implementation
    # Placeholder: Add actual test logic here later
    platform = MoodlePlatform.objects.get(pk=pk)
    messages.info(request, f"Connection test for {platform.name} not yet implemented.")
    return redirect('moodle_management:platform-detail', pk=pk)

# --- Your DRF ViewSets ---
class MoodlePlatformViewSet(viewsets.ModelViewSet):
    queryset = MoodlePlatform.objects.all()
    serializer_class = MoodlePlatformSerializer
    # Example permission: Allow any authenticated user to do anything, others read-only
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# --- Add other ViewSets mentioned in urls_api.py ---

# --- MoodleUser ViewSet ---
class MoodleUserViewSet(viewsets.ReadOnlyModelViewSet): # Example: ReadOnly
    queryset = MoodleUser.objects.all()
    serializer_class = MoodleUserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Example permission

# --- UserPlatformAssociation ViewSet ---
class UserPlatformAssociationViewSet(viewsets.ReadOnlyModelViewSet): # Example: ReadOnly
    queryset = UserPlatformAssociation.objects.all()
    serializer_class = UserPlatformAssociationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Example permission

# --- API Root View ---
@api_view(['GET'])
def api_root(request, format=None):
    """
    The entry endpoint of our API.
    """
    return Response({
        'platforms': reverse('moodleplatform-list', request=request, format=format),
        'users': reverse('moodleuser-list', request=request, format=format),
        'associations': reverse('userplatformassociation-list', request=request, format=format),
        'api-auth': reverse('rest_framework:login', request=request, format=format), # Link to login
    })
