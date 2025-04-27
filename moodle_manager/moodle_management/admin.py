from django.contrib import admin
from .models import MoodlePlatform, MoodleUser, UserPlatformAssociation

class UserPlatformAssociationInline(admin.TabularInline):
    model = UserPlatformAssociation
    extra = 1

class MoodleUserAdmin(admin.ModelAdmin):
    inlines = [UserPlatformAssociationInline]
    list_display = ('user', 'moodle_username', 'moodle_userid')
    search_fields = ('user__username', 'moodle_username')

class MoodlePlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'active', 'created_at')
    list_filter = ('active',)
    search_fields = ('name', 'url')

admin.site.register(MoodlePlatform, MoodlePlatformAdmin)
admin.site.register(MoodleUser, MoodleUserAdmin)
admin.site.register(UserPlatformAssociation)