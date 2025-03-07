from rest_framework import serializers
from burnout_prevention.analytics.models import StressLevel


class TrendSerializer(serializers.Serializer):
    """
    Сериализатор для данных о тренде.
    """
    value = serializers.FloatField()
    direction = serializers.CharField()


class StressLevelSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели уровня стресса.
    """
    class Meta:
        model = StressLevel
        fields = ['id', 'level', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class StressLevelCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания записи об уровне стресса.
    """
    class Meta:
        model = StressLevel
        fields = ['level', 'notes']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


class StressStatisticsSerializer(serializers.Serializer):
    """
    Сериализатор для статистики уровня стресса.
    """
    avg_level = serializers.FloatField()
    max_level = serializers.FloatField()
    min_level = serializers.FloatField()
    total_records = serializers.IntegerField()
    start_date = serializers.CharField()
    end_date = serializers.CharField()
    trend = TrendSerializer()
    statistics = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    ) 