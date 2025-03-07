from rest_framework import serializers
from burnout_prevention.analytics.models import BurnoutRisk


class BurnoutRiskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для риска выгорания.
    """
    # Добавляем виртуальные поля для удобства использования в API
    date = serializers.SerializerMethodField()
    work_hours_factor = serializers.SerializerMethodField()
    sleep_factor = serializers.SerializerMethodField()
    stress_factor = serializers.SerializerMethodField()
    breaks_factor = serializers.SerializerMethodField()
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
    
    def get_date(self, instance):
        """
        Возвращает дату создания записи.
        """
        return instance.created_at.date() if instance.created_at else None
        
    def get_work_hours_factor(self, instance):
        """
        Фактор рабочих часов (добавлен как виртуальное поле).
        По умолчанию возвращает 0, должен быть переопределен при необходимости.
        """
        return 0
        
    def get_sleep_factor(self, instance):
        """
        Фактор сна (добавлен как виртуальное поле).
        По умолчанию возвращает 0, должен быть переопределен при необходимости.
        """
        return 0
        
    def get_stress_factor(self, instance):
        """
        Фактор стресса (добавлен как виртуальное поле).
        По умолчанию возвращает 0, должен быть переопределен при необходимости.
        """
        return 0
        
    def get_breaks_factor(self, instance):
        """
        Фактор перерывов (добавлен как виртуальное поле).
        По умолчанию возвращает 0, должен быть переопределен при необходимости.
        """
        return 0
    
    def get_factors(self, instance):
        """
        Возвращает факторы риска в виде структурированного словаря.
        """
        return {
            'work_hours': self.get_work_hours_factor(instance),
            'sleep': self.get_sleep_factor(instance),
            'stress': self.get_stress_factor(instance),
            'breaks': self.get_breaks_factor(instance)
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