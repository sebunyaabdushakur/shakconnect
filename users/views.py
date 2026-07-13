from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings
from .models import Student
from .serializers import (
    RegisterSerializer,
    StudentProfileSerializer,
    StudentListSerializer,
    UpdateProfileSerializer
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.save()
            refresh = RefreshToken.for_user(student)
            return Response({
                'message': f'Welcome to Shak Connect, {student.full_name}!',
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
                'student': StudentProfileSerializer(student).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({
                'error': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        student = authenticate(request, email=email, password=password)

        if not student:
            return Response({
                'error': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if student.is_banned:
            return Response({
                'error': f'Your account has been suspended. Reason: {student.ban_reason}'
            }, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(student)
        return Response({
            'message': f'Welcome back, {student.full_name}!',
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'student': StudentProfileSerializer(student).data
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully'})
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = StudentProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        import cloudinary.uploader

        # Handle photo upload separately
        photo_url = None
        if 'profile_photo' in request.FILES:
            photo_file = request.FILES['profile_photo']
            result = cloudinary.uploader.upload(photo_file)
            photo_url = result.get('secure_url')

        # Update other fields
        data = request.data.copy()
        data.pop('profile_photo', None)

        serializer = UpdateProfileSerializer(
            request.user,
            data=data,
            partial=True
        )
        if serializer.is_valid():
            student = serializer.save()
            if photo_url:
                student.profile_photo = photo_url
                student.save()
            return Response({
                'message': 'Profile updated successfully',
                'student': StudentProfileSerializer(student).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentListSerializer

    def get_queryset(self):
        queryset = Student.objects.filter(
            is_active=True,
            is_banned=False
        ).exclude(id=self.request.user.id)

        course = self.request.query_params.get('course')
        year = self.request.query_params.get('year')
        search = self.request.query_params.get('search')

        if course:
            queryset = queryset.filter(course=course)
        if year:
            queryset = queryset.filter(year=year)
        if search:
            queryset = queryset.filter(full_name__icontains=search)

        return queryset


class StudentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            student = Student.objects.get(pk=pk, is_active=True, is_banned=False)
            serializer = StudentProfileSerializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)