from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Follow, Message
from .serializers import (
    FollowSerializer,
    MessageSerializer,
    ConversationSerializer
)
from users.models import Student


class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Follow a student
        try:
            student_to_follow = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        if student_to_follow == request.user:
            return Response({'error': 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)

        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=student_to_follow
        )

        if not created:
            return Response({'error': 'You are already following this student'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': f'You are now following {student_to_follow.full_name}'
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        # Unfollow a student
        try:
            student_to_unfollow = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            follow = Follow.objects.get(
                follower=request.user,
                following=student_to_unfollow
            )
            follow.delete()
            return Response({'message': f'You unfollowed {student_to_unfollow.full_name}'})
        except Follow.DoesNotExist:
            return Response({'error': 'You are not following this student'}, status=status.HTTP_400_BAD_REQUEST)


class FollowersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        followers = Follow.objects.filter(following=request.user)
        serializer = FollowSerializer(followers, many=True)
        return Response({
            'count': followers.count(),
            'followers': serializer.data
        })


class FollowingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        following = Follow.objects.filter(follower=request.user)
        serializer = FollowSerializer(following, many=True)
        return Response({
            'count': following.count(),
            'following': serializer.data
        })


class MessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all conversations
        sent = Message.objects.filter(sender=request.user).values_list('receiver', flat=True)
        received = Message.objects.filter(receiver=request.user).values_list('sender', flat=True)
        student_ids = set(list(sent) + list(received))
        students = Student.objects.filter(id__in=student_ids)
        serializer = ConversationSerializer(
            students,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    def post(self, request):
        # Send a message
        serializer = MessageSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            message = serializer.save()
            return Response({
                'message': 'Message sent!',
                'data': MessageSerializer(message).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # Get messages between two students
        try:
            other_student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        messages = Message.objects.filter(
            Q(sender=request.user, receiver=other_student) |
            Q(sender=other_student, receiver=request.user)
        ).order_by('created_at')

        # Mark messages as read
        messages.filter(receiver=request.user, is_read=False).update(is_read=True)

        serializer = MessageSerializer(messages, many=True)
        return Response({
            'student': other_student.full_name,
            'messages': serializer.data
        })


class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)

        total_students = Student.objects.filter(is_active=True).count()
        banned_students = Student.objects.filter(is_banned=True).count()
        total_messages = Message.objects.count()
        total_follows = Follow.objects.count()

        students_per_course = {}
        for course_code, course_name in Student.COURSE_CHOICES:
            count = Student.objects.filter(course=course_code, is_active=True).count()
            students_per_course[course_name] = count

        students_per_year = {}
        for year_code, year_name in Student.YEAR_CHOICES:
            count = Student.objects.filter(year=year_code, is_active=True).count()
            students_per_year[year_name] = count

        return Response({
            'total_students': total_students,
            'banned_students': banned_students,
            'total_messages': total_messages,
            'total_follows': total_follows,
            'students_per_course': students_per_course,
            'students_per_year': students_per_year,
        })


class BanStudentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not request.user.is_staff:
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)

        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        from django.utils import timezone
        student.is_banned = True
        student.ban_reason = request.data.get('reason', 'Violation of community guidelines')
        student.banned_at = timezone.now()
        student.save()

        return Response({
            'message': f'{student.full_name} has been banned',
            'reason': student.ban_reason
        })


class UnbanStudentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not request.user.is_staff:
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)

        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        student.is_banned = False
        student.ban_reason = ''
        student.banned_at = None
        student.save()

        return Response({'message': f'{student.full_name} has been unbanned'})