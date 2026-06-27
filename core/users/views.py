from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from .serializers import RegisterSerializer, UserProfileSerializer, UserProfileUpdateSerializer
from .models import User
from .permissions import IsAdmin
from children.models import ChildProfile
from reports.models import ASDReport, ADHDReport

class RegisterView(APIView):
    permission_classes = [AllowAny]  # anyone can register

    def post(self, request):
        # Validate the registration data using the serializer
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registration successful.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Authenticate the user using email and password
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)

        # If authentication is successful, generate JWT tokens and return user info
        if user:
            update_last_login(None, user)

            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'role': user.role,
                'name': f"{user.first_name} {user.last_name}",
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    # Retrieve and update user profile information
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    # Allow partial updates to the user profile
    def patch(self, request):
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]

    # Provide aggregated statistics for the admin dashboard
    def get(self, request):
        # Compute average age in Python to avoid PostgreSQL subquery wrapping issues
        all_ages = [
            c.basic_info.get('age')
            for c in ChildProfile.objects.only('basic_info')
            if c.basic_info and c.basic_info.get('age') is not None
        ]
        average_child_age = round(sum(all_ages) / len(all_ages), 1) if all_ages else None
        
        data = {
            'total_children': ChildProfile.objects.count(),
            'total_parents': User.objects.filter(role='parent').count(),
            'total_doctors': User.objects.filter(role='doctor').count(),
            'average_child_age': average_child_age,
            'total_asd_reports': ASDReport.objects.count(),
            'total_adhd_reports': ADHDReport.objects.count(),
            'asd_high_risk_count': ASDReport.objects.filter(
                Q(videos_risk_level__iexact='HIGH') |
                Q(physiology_risk_level__iexact='HIGH')
            ).count(),
            'adhd_high_risk_count': ADHDReport.objects.filter(risk_level='HIGH').count(),
        }
        return Response(data)

class UserDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    # Provide user-specific statistics for the dashboard
    def get(self, request):
        user = request.user
        children = ChildProfile.objects.filter(
            Q(created_by=user) |
            Q(authorized_doctors__doctor=user)
        ).distinct()

        # Compute average age in Python to avoid PostgreSQL subquery wrapping issues
        ages = [
            c.basic_info.get('age')
            for c in children
            if c.basic_info and c.basic_info.get('age') is not None
        ]
        average_age = round(sum(ages) / len(ages), 1) if ages else None

        data = {
            'total_children': children.count(),
            'average_age': average_age,
            'children_with_asd_report': children.filter(asd_report__isnull=False).count(),
            'children_with_adhd_report': children.filter(adhd_report__isnull=False).count(),
        }
        return Response(data)