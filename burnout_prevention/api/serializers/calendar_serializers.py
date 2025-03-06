from rest_framework import serializers
from burnout_prevention.integrations.models import CalendarIntegration, CalendarEvent


class CalendarIntegrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для интеграции с календарем.
    """
    class Meta:
        model = CalendarIntegration
        fields = ['id', 'user', 'type', 'access_token', 'refresh_token', 'token_expiry', 'is_active', 'last_sync', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class CalendarEventSerializer(serializers.ModelSerializer):
    """
    Сериализатор для событий календаря.
    """
    class Meta:
        model = CalendarEvent
        fields = [
            'id', 'integration', 'event_id', 'title', 'description',
            'start_time', 'end_time', 'location', 'is_all_day', 
            'is_meeting', 'attendees_count', 'stress_score',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 