from rest_framework import serializers
from burnout_prevention.analytics.models import BurnoutRisk


class BurnoutRiskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для риска выгорания.
    """
    # Добавляем виртуальные поля для удобства использования в API
    factors = serializers.SerializerMethodField()
    recommendations = serializers.SerializerMethodField(required=False)
    
    class Meta:
        model = BurnoutRisk
        fields = [
            'id', 'user', 'date', 'risk_level', 
            'work_hours_factor', 'sleep_factor', 'stress_factor', 'breaks_factor',
            'factors', 'recommendations', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def get_factors(self, instance):
        """
        Возвращает факторы риска в виде структурированного словаря.
        """
        return {
            'work_hours': instance.work_hours_factor,
            'sleep': instance.sleep_factor,
            'stress': instance.stress_factor,
            'breaks': instance.breaks_factor
        }
    
    def get_recommendations(self, instance):
        """
        Формирует рекомендации на основе факторов риска.
        По умолчанию - пустой список, переопределяется в представлении.
        """
        return []

    def to_representation(self, instance):
        """
        Расширенное представление данных модели.
        """
        representation = super().to_representation(instance)
        # Дополнительная обработка, если необходимо
        return representation 