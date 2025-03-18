from rest_framework import serializers
from burnout_prevention.analytics.models import BurnoutRisk


class BurnoutRiskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для риска выгорания.
    """
    # Добавляем виртуальные поля для удобства использования в API
    date = serializers.SerializerMethodField()
    overtime_factor = serializers.SerializerMethodField()
    workday_duration_factor = serializers.SerializerMethodField()
    stress_factor = serializers.SerializerMethodField()
    sleep_quality_factor = serializers.SerializerMethodField()
    sleep_deprivation_factor = serializers.SerializerMethodField()
    factors_data = serializers.SerializerMethodField()
    recommendations = serializers.SerializerMethodField(required=False)
    
    class Meta:
        model = BurnoutRisk
        fields = [
            'id', 'user', 'date', 'risk_level', 
            'overtime_factor', 'workday_duration_factor', 'stress_factor', 
            'sleep_quality_factor', 'sleep_deprivation_factor',
            'factors_data', 'recommendations', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def get_date(self, instance):
        """
        Возвращает дату создания записи.
        """
        return instance.created_at.date() if instance.created_at else None
        
    def get_overtime_factor(self, instance):
        """
        Возвращает фактор переработки.
        """
        if hasattr(instance, 'factors') and instance.factors:
            return instance.factors.get('overtime', {}).get('value', 0)
        return 0
        
    def get_workday_duration_factor(self, instance):
        """
        Возвращает фактор длительности рабочего дня.
        """
        if hasattr(instance, 'factors') and instance.factors:
            return instance.factors.get('workday_duration', {}).get('value', 0)
        return 0
        
    def get_stress_factor(self, instance):
        """
        Возвращает фактор стресса.
        """
        if hasattr(instance, 'factors') and instance.factors:
            return instance.factors.get('stress', {}).get('value', 0)
        return 0
        
    def get_sleep_quality_factor(self, instance):
        """
        Возвращает фактор качества сна.
        """
        if hasattr(instance, 'factors') and instance.factors:
            return instance.factors.get('sleep_quality', {}).get('value', 0)
        return 0
        
    def get_sleep_deprivation_factor(self, instance):
        """
        Возвращает фактор недосыпа.
        """
        if hasattr(instance, 'factors') and instance.factors:
            return instance.factors.get('sleep_deprivation', {}).get('value', 0)
        return 0
    
    def get_factors_data(self, instance):
        """
        Возвращает факторы риска в виде структурированного словаря.
        """
        return {
            'overtime': self.get_overtime_factor(instance),
            'workday_duration': self.get_workday_duration_factor(instance),
            'stress': self.get_stress_factor(instance),
            'sleep_quality': self.get_sleep_quality_factor(instance),
            'sleep_deprivation': self.get_sleep_deprivation_factor(instance)
        }
    
    def get_recommendations(self, instance):
        """
        Формирует рекомендации на основе факторов риска.
        """
        if hasattr(instance, 'recommendations') and instance.recommendations:
            return instance.recommendations
        return []

    def to_representation(self, instance):
        """
        Расширенное представление данных модели.
        """
        representation = super().to_representation(instance)
        # Добавляем веса факторов
        representation['factors_weights'] = {
            'overtime': 0.15,
            'workday_duration': 0.10,
            'stress': 0.20,
            'sleep_quality': 0.20,
            'sleep_deprivation': 0.20
        }
        return representation 