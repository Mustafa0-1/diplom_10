from typing import Any

from django.contrib.auth import login, logout
from rest_framework import generics
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from todolist.core.models import User
from todolist.core.serializers import CreateUserSerializer, LoginSerializer, ProfileSerializer, UpdatePasswordSerializer


class SignupView(generics.CreateAPIView):
    """Ручка для регистрации нового пользователя"""
    serializer_class = CreateUserSerializer


class LoginView(generics.CreateAPIView):
    """Ручка для входа пользователя"""
    serializer_class = LoginSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Метод производит вход(login) пользователя"""
        serializer: LoginSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        login(request=request, user=serializer.save())
        return Response(serializer.data)


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    """Ручка для отображения, редактирования и выхода пользователя"""
    serializer_class: Serializer = ProfileSerializer
    permission_classes: tuple[BasePermission, ...] = (IsAuthenticated,)

    def get_object(self):
        """Метод возвращает объект пользователя из БД"""
        return self.request.user

    def perform_destroy(self, instance: User):
        """Метод производит выход(logout) пользователя"""
        logout(self.request)


class UpdatePasswordView(generics.UpdateAPIView):
    """Ручка для смены пароля пользователя"""
    permission_classes: tuple[BasePermission, ...] = (IsAuthenticated,)
    serializer_class: Serializer = UpdatePasswordSerializer

    def get_object(self):
        """Метод возвращает объект пользователя из БД"""
        return self.request.user
