from django.db import models
from django.contrib.auth.models import User

class MoodlePlatform(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(unique=True)
    api_key = models.CharField(max_length=100)
    api_endpoint = models.CharField(max_length=100, default='/webservice/rest/server.php')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Moodle Platform"
        verbose_name_plural = "Moodle Platforms"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class MoodleUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    moodle_username = models.CharField(max_length=100, blank=True, null=True)
    moodle_userid = models.IntegerField(blank=True, null=True)
    platforms = models.ManyToManyField(MoodlePlatform, through='UserPlatformAssociation')
    
    def __str__(self):
        return f"{self.user.username} - Moodle User"

class UserPlatformAssociation(models.Model):
    user = models.ForeignKey(MoodleUser, on_delete=models.CASCADE)
    platform = models.ForeignKey(MoodlePlatform, on_delete=models.CASCADE)
    platform_userid = models.IntegerField()
    platform_username = models.CharField(max_length=100)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'platform')
    
    def __str__(self):
        return f"{self.user.user.username} on {self.platform.name}"