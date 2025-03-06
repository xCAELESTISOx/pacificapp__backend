from rest_framework import serializers
from burnout_prevention.users.models import User, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользователей.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login', 
                  'date_of_birth', 'avatar', 'stress_level_base', 'sleep_hours_avg', 'work_hours_daily',
                  'notifications_enabled', 'notification_frequency']
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для профилей пользователей.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'preferred_relaxation_methods', 
            'work_start_time', 'work_end_time',
            'google_calendar_connected', 'outlook_connected',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
        

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления профиля пользователя.
    """
    class Meta:
        model = UserProfile
        fields = [
            'preferred_relaxation_methods', 
            'work_start_time', 'work_end_time',
            'google_calendar_connected', 'outlook_connected'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """
    Сериализатор для изменения пароля пользователя.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    
    def validate_old_password(self, value):
        """
        Проверяет, что старый пароль корректен.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class UserNotificationSettingsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для настроек уведомлений.
    """
    class Meta:
        model = User
        fields = ['notifications_enabled', 'notification_frequency'] 