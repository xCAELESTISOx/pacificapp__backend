from rest_framework import serializers
from burnout_prevention.analytics.models import WorkActivity


class WorkActivitySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели рабочей активности.
    """
    class Meta:
        model = WorkActivity
        fields = ['id', 'date', 'duration_hours', 'breaks_count', 'breaks_total_minutes', 'productivity', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class WorkActivityCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания записи о рабочей активности.
    """
    class Meta:
        model = WorkActivity
        fields = ['date', 'duration_hours', 'breaks_count', 'breaks_total_minutes', 'productivity', 'notes']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


class DailyWorkDataSerializer(serializers.Serializer):
    """
    Сериализатор для ежедневных данных рабочей активности.
    """
    date = serializers.CharField()
    duration_hours = serializers.FloatField()
    productivity = serializers.FloatField(allow_null=True)
    notes = serializers.CharField(allow_null=True, allow_blank=True)


class WorkStatisticsSerializer(serializers.Serializer):
    """
    Сериализатор для статистики рабочей активности.
    """
    average_duration = serializers.FloatField()
    average_productivity = serializers.FloatField(allow_null=True)
    average_breaks_count = serializers.FloatField(allow_null=True)
    average_breaks_duration = serializers.FloatField(allow_null=True)
    total_records = serializers.IntegerField()
    start_date = serializers.CharField()
    end_date = serializers.CharField()
    daily_data = serializers.ListField(
        child=DailyWorkDataSerializer()
    ) 