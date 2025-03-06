from rest_framework import serializers
from burnout_prevention.analytics.models import StressLevel, SleepRecord, WorkActivity, BurnoutRisk


class TrendSerializer(serializers.Serializer):
    value = serializers.FloatField()
    direction = serializers.CharField()

class SleepDataSerializer(serializers.Serializer):
    average_duration = serializers.FloatField()
    average_quality = serializers.FloatField(allow_null=True)
    total_records = serializers.IntegerField()
    trend = TrendSerializer()

class StressDataSerializer(serializers.Serializer):
    average_level = serializers.FloatField()
    total_records = serializers.IntegerField()
    trend = TrendSerializer()

class WorkDataSerializer(serializers.Serializer):
    average_duration = serializers.FloatField()
    average_productivity = serializers.FloatField(allow_null=True)
    total_records = serializers.IntegerField()
    trend = TrendSerializer()

class RecommendationItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    category = serializers.CharField()
    status = serializers.CharField()

class RecommendationsDataSerializer(serializers.Serializer):
    pending = serializers.IntegerField()
    completed = serializers.IntegerField()
    accepted = serializers.IntegerField()
    latest = RecommendationItemSerializer(many=True)

class BurnoutRiskSerializer(serializers.Serializer):
    current = serializers.IntegerField()
    previous = serializers.IntegerField(allow_null=True, required=False)
    trend = TrendSerializer()

class DashboardSerializer(serializers.Serializer):
    """
    Сериализатор для панели мониторинга, объединяющий данные из разных источников.
    """
    sleep = SleepDataSerializer()
    stress = StressDataSerializer()
    work = WorkDataSerializer()
    recommendations = RecommendationsDataSerializer()
    burnout_risk = BurnoutRiskSerializer(allow_null=True) 