from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response

from burnout_prevention.analytics.models import (
    BurnoutRisk, 
    StressLevel, 
    SleepRecord, 
    WorkActivity
)
from burnout_prevention.users.models import UserProfile
from ..serializers.burnout_serializers import BurnoutRiskSerializer


class BurnoutRiskViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра риска выгорания.
    """
    queryset = BurnoutRisk.objects.all()
    serializer_class = BurnoutRiskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает только записи текущего пользователя.
        """
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """
        Рассчитывает текущий риск выгорания для пользователя.
        """
        user = request.user
        now = timezone.now()
        month_ago = now - timedelta(days=30)
        
        # Получаем данные пользователя
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Получаем данные о стрессе за последний месяц
        stress_data = StressLevel.objects.filter(
            user=user,
            created_at__gte=month_ago
        )
        avg_stress = stress_data.aggregate(avg=Avg('level'))['avg'] or 0
        stress_count = stress_data.count()
        
        # Получаем данные о сне за последний месяц
        sleep_data = SleepRecord.objects.filter(
            user=user,
            date__gte=month_ago.date()
        )
        avg_sleep_duration = sleep_data.aggregate(avg=Avg('duration_hours'))['avg'] or 0
        avg_sleep_quality = sleep_data.aggregate(avg=Avg('quality'))['avg'] or 0
        sleep_count = sleep_data.count()
        
        # Получаем данные о работе за последний месяц
        work_data = WorkActivity.objects.filter(
            user=user,
            date__gte=month_ago.date()
        )
        avg_work_duration = work_data.aggregate(avg=Avg('duration_hours'))['avg'] or 0
        avg_breaks = work_data.aggregate(avg=Avg('breaks_count'))['avg'] or 0
        avg_productivity = work_data.aggregate(avg=Avg('productivity'))['avg'] or 0
        work_count = work_data.count()
        
        # Рассчитываем риск выгорания на основе полученных данных
        # Это упрощенная модель, в реальном приложении здесь может быть сложный алгоритм
        
        # Факторы риска:
        # 1. Высокий уровень стресса
        # 2. Недостаток сна (менее 7 часов)
        # 3. Низкое качество сна
        # 4. Длительное рабочее время (более 8 часов)
        # 5. Мало перерывов
        # 6. Низкая продуктивность
        
        risk_factors = {}
        risk_level = 0
        
        # Оценка стресса (0-10)
        if avg_stress > 7:
            risk_factors['high_stress'] = {
                'level': 'high',
                'value': avg_stress,
                'weight': 0.3
            }
            risk_level += avg_stress * 0.3
        elif avg_stress > 5:
            risk_factors['medium_stress'] = {
                'level': 'medium',
                'value': avg_stress,
                'weight': 0.2
            }
            risk_level += avg_stress * 0.2
        
        # Оценка сна (0-10)
        sleep_risk = 0
        if avg_sleep_duration < 6:
            risk_factors['insufficient_sleep'] = {
                'level': 'high',
                'value': avg_sleep_duration,
                'weight': 0.25
            }
            sleep_risk += 3
        elif avg_sleep_duration < 7:
            risk_factors['low_sleep'] = {
                'level': 'medium',
                'value': avg_sleep_duration,
                'weight': 0.15
            }
            sleep_risk += 2
            
        if avg_sleep_quality < 5:
            risk_factors['poor_sleep_quality'] = {
                'level': 'high',
                'value': avg_sleep_quality,
                'weight': 0.2
            }
            sleep_risk += 3
        elif avg_sleep_quality < 7:
            risk_factors['medium_sleep_quality'] = {
                'level': 'medium',
                'value': avg_sleep_quality,
                'weight': 0.1
            }
            sleep_risk += 2
            
        risk_level += sleep_risk * 0.25
        
        # Оценка работы (0-10)
        work_risk = 0
        if avg_work_duration > 10:
            risk_factors['excessive_work'] = {
                'level': 'high',
                'value': avg_work_duration,
                'weight': 0.25
            }
            work_risk += 3
        elif avg_work_duration > 8:
            risk_factors['long_work'] = {
                'level': 'medium',
                'value': avg_work_duration,
                'weight': 0.15
            }
            work_risk += 2
            
        if avg_breaks < 2:
            risk_factors['few_breaks'] = {
                'level': 'high',
                'value': avg_breaks,
                'weight': 0.15
            }
            work_risk += 3
        elif avg_breaks < 4:
            risk_factors['medium_breaks'] = {
                'level': 'medium',
                'value': avg_breaks,
                'weight': 0.1
            }
            work_risk += 2
            
        if avg_productivity < 5:
            risk_factors['low_productivity'] = {
                'level': 'high',
                'value': avg_productivity,
                'weight': 0.2
            }
            work_risk += 3
        elif avg_productivity < 7:
            risk_factors['medium_productivity'] = {
                'level': 'medium',
                'value': avg_productivity,
                'weight': 0.1
            }
            work_risk += 2
            
        risk_level += work_risk * 0.25
        
        # Нормализуем риск до шкалы 0-10
        risk_level = min(max(risk_level, 0), 10)
        
        # Формируем рекомендации на основе факторов риска
        recommendations = []
        
        if 'high_stress' in risk_factors or 'medium_stress' in risk_factors:
            recommendations.append({
                'type': 'stress',
                'title': 'Снижение уровня стресса',
                'description': 'Рекомендуется практиковать техники релаксации и медитации для снижения уровня стресса.'
            })
            
        if 'insufficient_sleep' in risk_factors or 'low_sleep' in risk_factors:
            recommendations.append({
                'type': 'sleep',
                'title': 'Увеличение продолжительности сна',
                'description': 'Старайтесь спать не менее 7-8 часов в сутки для полноценного отдыха.'
            })
            
        if 'poor_sleep_quality' in risk_factors or 'medium_sleep_quality' in risk_factors:
            recommendations.append({
                'type': 'sleep',
                'title': 'Улучшение качества сна',
                'description': 'Создайте комфортные условия для сна: тихая комната, удобная кровать, отсутствие яркого света.'
            })
            
        if 'excessive_work' in risk_factors or 'long_work' in risk_factors:
            recommendations.append({
                'type': 'work',
                'title': 'Сокращение рабочего времени',
                'description': 'Постарайтесь ограничить рабочее время до 8 часов в день, делегируйте задачи, если возможно.'
            })
            
        if 'few_breaks' in risk_factors or 'medium_breaks' in risk_factors:
            recommendations.append({
                'type': 'work',
                'title': 'Увеличение количества перерывов',
                'description': 'Делайте короткие перерывы каждые 1-2 часа работы для отдыха и восстановления.'
            })
            
        if 'low_productivity' in risk_factors or 'medium_productivity' in risk_factors:
            recommendations.append({
                'type': 'work',
                'title': 'Повышение продуктивности',
                'description': 'Используйте техники тайм-менеджмента, устраняйте отвлекающие факторы, приоритизируйте задачи.'
            })
        
        # Создаем запись о риске выгорания
        burnout_risk = BurnoutRisk.objects.create(
            user=user,
            risk_level=risk_level,
            factors=risk_factors,
            recommendations=recommendations
        )
        
        serializer = BurnoutRiskSerializer(burnout_risk)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        Возвращает последнюю оценку риска выгорания.
        """
        user = request.user
        latest_risk = BurnoutRisk.objects.filter(user=user).order_by('-created_at').first()
        
        if not latest_risk:
            return Response(
                {"detail": "No burnout risk assessment found"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = BurnoutRiskSerializer(latest_risk)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Возвращает историю оценок риска выгорания.
        """
        user = request.user
        risks = BurnoutRisk.objects.filter(user=user).order_by('-created_at')
        
        serializer = BurnoutRiskSerializer(risks, many=True)
        return Response(serializer.data) 