from django.urls import path
from .views import (
    FollowView,
    FollowersView,
    FollowingView,
    MessageView,
    ConversationView,
    AdminStatsView,
    BanStudentView,
    UnbanStudentView,
)

urlpatterns = [
    path('follow/<int:pk>/', FollowView.as_view(), name='follow'),
    path('followers/', FollowersView.as_view(), name='followers'),
    path('following/', FollowingView.as_view(), name='following'),
    path('messages/', MessageView.as_view(), name='messages'),
    path('messages/<int:pk>/', ConversationView.as_view(), name='conversation'),
    path('admin/stats/', AdminStatsView.as_view(), name='admin_stats'),
    path('admin/ban/<int:pk>/', BanStudentView.as_view(), name='ban_student'),
    path('admin/unban/<int:pk>/', UnbanStudentView.as_view(), name='unban_student'),
]