from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from ..serializers import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def profile(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def deactivate(self, request):
        user = request.user
        if not user.is_active:
            return Response({'detail': 'Account already inactive.'}, status=status.HTTP_200_OK)
        user.is_active = False
        user.save(update_fields=['is_active'])
        Token.objects.filter(user=user).delete()
        return Response({'detail': 'Account deactivated.'}, status=status.HTTP_200_OK)


