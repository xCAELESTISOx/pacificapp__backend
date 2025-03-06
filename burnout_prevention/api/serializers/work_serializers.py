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


class WorkStatisticsSerializer(serializers.Serializer):
    """
    Сериализатор для статистики рабочей активности.
    """
    avg_duration = serializers.FloatField()
    avg_breaks = serializers.FloatField()
    avg_breaks_duration = serializers.FloatField()
    avg_productivity = serializers.FloatField()
    total_records = serializers.IntegerField()
    statistics = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    ) 