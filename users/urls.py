from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    MyProfileView,
    StudentListView,
    StudentDetailView,
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('profile/me/', MyProfileView.as_view(), name='my_profile'),
    path('students/', StudentListView.as_view(), name='student_list'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
]