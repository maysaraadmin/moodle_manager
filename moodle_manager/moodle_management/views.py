from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
from .models import MoodlePlatform, MoodleUser, UserPlatformAssociation
from .serializers import MoodlePlatformSerializer, MoodleUserSerializer, UserPlatformAssociationSerializer
from .utils import MoodleAPI
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        'platforms': reverse('moodleplatform-list', request=request, format=format),
        'users': reverse('moodleuser-list', request=request, format=format),
        'admin': reverse('admin:index', request=request, format=format),
        'login': reverse('rest_framework:login', request=request, format=format),
        'logout': reverse('rest_framework:logout', request=request, format=format),
        'token_auth': reverse('api_token_auth', request=request, format=format),
    })

class MoodlePlatformViewSet(viewsets.ModelViewSet):
    queryset = MoodlePlatform.objects.all()
    serializer_class = MoodlePlatformSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=True, methods=['get'])
    def test_connection(self, request, pk=None):
        platform = self.get_object()
        moodle_api = MoodleAPI(platform.id)
        site_info = moodle_api.get_site_info()
        
        if site_info:
            return Response({'status': 'success', 'data': site_info})
        return Response({'status': 'error', 'message': 'Could not connect to Moodle platform'}, 
                      status=status.HTTP_400_BAD_REQUEST)

class MoodleUserViewSet(viewsets.ModelViewSet):
    queryset = MoodleUser.objects.all()
    serializer_class = MoodleUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return MoodleUser.objects.all()
        return MoodleUser.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def sync_platforms(self, request, pk=None):
        moodle_user = self.get_object()
        platforms = moodle_user.platforms.all()
        
        results = []
        for platform in platforms:
            moodle_api = MoodleAPI(platform.id)
            user_data = moodle_api.get_user_by_field('username', moodle_user.moodle_username)
            
            if user_data:
                association, created = UserPlatformAssociation.objects.get_or_create(
                    user=moodle_user,
                    platform=platform,
                    defaults={
                        'platform_userid': user_data[0]['id'],
                        'platform_username': user_data[0]['username']
                    }
                )
                
                if not created:
                    association.platform_userid = user_data[0]['id']
                    association.platform_username = user_data[0]['username']
                    association.save()
                
                results.append({
                    'platform': platform.name,
                    'status': 'success',
                    'user_id': user_data[0]['id']
                })
            else:
                results.append({
                    'platform': platform.name,
                    'status': 'error',
                    'message': 'User not found on this platform'
                })
        
        return Response(results)

class UserPlatformAssociationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserPlatformAssociationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserPlatformAssociation.objects.all()
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return UserPlatformAssociation.objects.all()
        return UserPlatformAssociation.objects.filter(user__user=self.request.user)
    


class MoodlePlatformListView(ListView):
    model = MoodlePlatform
    template_name = 'moodle_management/platform_list.html'
    context_object_name = 'platforms'

class MoodlePlatformCreateView(CreateView):
    model = MoodlePlatform
    template_name = 'moodle_management/platform_form.html'
    fields = ['name', 'url', 'api_key', 'active']
    success_url = reverse_lazy('platform-list')

    def form_valid(self, form):
        messages.success(self.request, 'Platform added successfully!')
        return super().form_valid(form)

class MoodlePlatformUpdateView(UpdateView):
    model = MoodlePlatform
    template_name = 'moodle_management/platform_form.html'
    fields = ['name', 'url', 'api_key', 'active']
    success_url = reverse_lazy('platform-list')

    def form_valid(self, form):
        messages.success(self.request, 'Platform updated successfully!')
        return super().form_valid(form)

class MoodlePlatformDetailView(DetailView):
    model = MoodlePlatform
    template_name = 'moodle_management/platform_detail.html'
    context_object_name = 'platform'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test_result'] = self.request.session.get('test_result')
        if 'test_result' in self.request.session:
            del self.request.session['test_result']
        return context

class MoodlePlatformDeleteView(DeleteView):
    model = MoodlePlatform
    success_url = reverse_lazy('platform-list')
    template_name = 'moodle_management/platform_confirm_delete.html'

    def form_valid(self, form):
        messages.success(self.request, 'Platform deleted successfully!')
        return super().form_valid(form)

def test_connection(request, pk):
    platform = MoodlePlatform.objects.get(pk=pk)
    moodle_api = MoodleAPI(platform.id)
    site_info = moodle_api.get_site_info()
    
    if site_info:
        request.session['test_result'] = {
            'success': True,
            'message': 'Successfully connected to Moodle platform!',
            'data': site_info
        }
    else:
        request.session['test_result'] = {
            'success': False,
            'message': 'Failed to connect to Moodle platform'
        }
    
    return redirect('platform-detail', pk=pk)