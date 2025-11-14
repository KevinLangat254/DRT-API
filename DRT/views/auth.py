from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth import authenticate

from ..serializers import RegistrationSerializer, UserSerializer

User = get_user_model()


class RegisterAPIView(GenericAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
    
class LoginAPIView(GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {"detail": "Please provide both username and password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user": UserSerializer(user).data
            },
            status=status.HTTP_200_OK
        )    



class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({'detail': 'Logged out'}, status=status.HTTP_200_OK)
    


def web_logout(request):
    auth_logout(request)
    return redirect('login')


