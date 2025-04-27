from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import MoodlePlatform

class MoodlePlatformListView(ListView):
    model = MoodlePlatform
    template_name = 'moodle_management/platform_list.html'
    context_object_name = 'platforms'

class MoodlePlatformCreateView(CreateView):
    model = MoodlePlatform
    template_name = 'moodle_management/platform_form.html'
    fields = ['name', 'url', 'api_key', 'active']
    success_url = reverse_lazy('moodle_management:platform-list')

class MoodlePlatformUpdateView(UpdateView):
    model = MoodlePlatform
    template_name = 'moodle_management/platform_form.html'
    fields = ['name', 'url', 'api_key', 'active']
    success_url = reverse_lazy('moodle_management:platform-list')

class MoodlePlatformDetailView(DetailView):
    model = MoodlePlatform
    template_name = 'moodle_management/platform_detail.html'

class MoodlePlatformDeleteView(DeleteView):
    model = MoodlePlatform
    template_name = 'moodle_management/platform_confirm_delete.html'
    success_url = reverse_lazy('moodle_management:platform-list')

def test_connection(request, pk):
    # Your test connection implementation
    return redirect('moodle_management:platform-detail', pk=pk)