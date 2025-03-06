from rest_framework import serializers
from burnout_prevention.analytics.models import SleepRecord


class SleepRecordSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели записи о сне.
    """
    class Meta:
        model = SleepRecord
        fields = ['id', 'date', 'duration_hours', 'quality', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class SleepRecordCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания записи о сне.
    """
    class Meta:
        model = SleepRecord
        fields = ['date', 'duration_hours', 'quality', 'notes']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


class SleepStatisticsSerializer(serializers.Serializer):
    """
    Сериализатор для статистики сна.
    """
    avg_duration = serializers.FloatField()
    avg_quality = serializers.FloatField()
    total_records = serializers.IntegerField()
    statistics = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    ) 