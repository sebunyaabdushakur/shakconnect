from django.contrib import admin
from .models import Follow, Message


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    search_fields = ['follower__full_name', 'following__full_name']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'content', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['sender__full_name', 'receiver__full_name', 'content']