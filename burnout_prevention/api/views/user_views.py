from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import update_session_auth_hash
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from burnout_prevention.users.models import User, UserProfile, UserActivity
from ..serializers.user_serializers import (
    UserSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    PasswordChangeSerializer,
    UserNotificationSettingsSerializer
)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API точки доступа для управления пользователями.
    
    Предоставляет функциональность для просмотра и редактирования пользовательских данных,
    обновления профиля, изменения пароля и управления настройками.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает только текущего пользователя, если это не админ.
        """
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return User.objects.filter(id=user.id)
    
    @swagger_auto_schema(
        operation_description="Получить профиль текущего авторизованного пользователя",
        responses={200: UserProfileSerializer}
    )
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """
        Возвращает профиль текущего пользователя.
        
        Этот эндпоинт предоставляет доступ к полным данным профиля, включая
        личную информацию, настройки и предпочтения.
        """
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        methods=['get'],
        operation_description="Получить данные текущего пользователя",
        responses={200: UserProfileSerializer}
    )
    @swagger_auto_schema(
        methods=['patch'],
        operation_description="Обновить данные текущего пользователя",
        request_body=UserProfileUpdateSerializer,
        responses={
            200: UserProfileSerializer,
            400: "Неверные данные"
        }
    )
    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """
        Получение или обновление данных текущего пользователя.
        
        GET: Возвращает профиль текущего пользователя.
        PATCH: Частично обновляет данные профиля пользователя.
        """
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(UserProfileSerializer(profile).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        methods=['put', 'patch'],
        operation_description="Обновить профиль текущего пользователя",
        request_body=UserProfileUpdateSerializer,
        responses={
            200: UserProfileSerializer,
            400: "Неверные данные"
        }
    )
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """
        Обновляет профиль текущего пользователя.
        
        Принимает полные или частичные данные профиля и обновляет 
        соответствующие поля. Для частичного обновления используйте PATCH,
        для полного обновления - PUT.
        """
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(UserProfileSerializer(profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Изменить пароль пользователя",
        request_body=PasswordChangeSerializer,
        responses={
            200: openapi.Response(
                description="Пароль успешно изменен",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Неверные данные"
        }
    )
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Изменяет пароль текущего пользователя.
        
        Требует предоставления текущего пароля для подтверждения личности
        и нового пароля с подтверждением.
        """
        user = request.user
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)  # Сохраняем текущую сессию
            return Response({"detail": "Password changed successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Получить историю активности пользователя",
        responses={
            200: openapi.Response(
                description="Список действий пользователя",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'activity_type': openapi.Schema(type=openapi.TYPE_STRING),
                            'description': openapi.Schema(type=openapi.TYPE_STRING),
                            'timestamp': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                        }
                    )
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def activity(self, request):
        """
        Возвращает историю активности пользователя.
        
        Предоставляет список последних действий, выполненных пользователем
        в системе, отсортированный по времени (от новых к старым).
        """
        user = request.user
        activities = UserActivity.objects.filter(user=user).order_by('-timestamp')[:50]  # Последние 50 активностей
        
        # Здесь нужен сериализатор для UserActivity, но мы его пока не создали
        # В качестве примера возвращаем простое представление
        activity_data = [
            {
                'id': activity.id,
                'activity_type': activity.activity_type,
                'description': activity.description,
                'timestamp': activity.timestamp.isoformat()
            }
            for activity in activities
        ]
        
        return Response(activity_data)
    
    @swagger_auto_schema(
        methods=['put', 'patch'],
        operation_description="Обновить настройки уведомлений",
        request_body=UserNotificationSettingsSerializer,
        responses={
            200: UserNotificationSettingsSerializer,
            400: "Неверные данные"
        }
    )
    @action(detail=False, methods=['put', 'patch'])
    def notification_settings(self, request):
        """
        Обновляет настройки уведомлений пользователя.
        """
        user = request.user
        serializer = UserNotificationSettingsSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Загрузить аватар пользователя",
        manual_parameters=[
            openapi.Parameter(
                'avatar',
                openapi.IN_FORM,
                description="Изображение для аватара профиля",
                type=openapi.TYPE_FILE,
                required=True
            )
        ],
        responses={
            200: UserProfileSerializer,
            400: "Файл не предоставлен или имеет неверный формат"
        },
        consumes=['multipart/form-data']
    )
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_avatar(self, request):
        """
        Загружает аватар пользователя.
        
        Принимает файл изображения и устанавливает его как аватар
        текущего пользователя.
        """
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if 'avatar' not in request.FILES:
            return Response({"error": "No avatar file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        profile.avatar = request.FILES['avatar']
        profile.save()
        
        return Response(UserProfileSerializer(profile).data)
    
    @swagger_auto_schema(
        operation_description="Удалить аккаунт пользователя",
        responses={
            200: openapi.Response(
                description="Аккаунт успешно деактивирован",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['post'])
    def delete_account(self, request):
        """
        Удаляет аккаунт пользователя.
        
        Выполняет мягкое удаление аккаунта, деактивируя его,
        но сохраняя все данные в системе.
        """
        user = request.user
        user.is_active = False  # Мягкое удаление, сохраняем данные
        user.save()
        
        return Response({"detail": "Account deactivated successfully"}, status=status.HTTP_200_OK) 