from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta, datetime
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
    
    def _calculate_burnout_risk(self, user, date=None):
        """
        Рассчитывает риск выгорания для пользователя на указанную дату.
        Если дата не указана, используется текущая дата.
        Не сохраняет данные в базу данных.
        
        Баллы переработки = фактические часы переработки
        Баллы Длительности рабочего дня = max(0, (фактические часы - 8) * 0.4)
        Баллы Собственной оценка стресса = Оценка стресса пользователя / 10
        Баллы Качества сна = 10 - оценка качества сна пользователем
        Баллы недосыпа = min((8 - кол-во часов сна)*0.4, 10)
        
        Веса факторов:
        Переработки - 0.15
        Длительность рабочего дня - 0.10
        Собственная оценка стресса - 0.20
        Качество сна - 0.20
        Недосып - 0.20
        
        Returns:
            dict: Словарь с данными о риске выгорания
        """
        if date is None:
            date = timezone.now().date()
            
        # Получаем данные о работе за последний день для указанной даты
        latest_work = WorkActivity.objects.filter(
            user=user,
            date__lte=date
        ).order_by('-date').first()
        
        work_hours = latest_work.duration_hours if latest_work else 8
        overtime_hours = max(0, work_hours - 8)
        
        # Рассчитываем баллы по каждому фактору
        overtime_points = overtime_hours  # Баллы переработки = фактические часы переработки
        workday_duration_points = max(0, (work_hours - 8) * 0.4)  # Баллы длительности рабочего дня
        
        # Получаем данные о стрессе для указанной даты
        latest_stress = StressLevel.objects.filter(
            user=user,
            created_at__date__lte=date
        ).order_by('-created_at').first()
        
        stress_level = latest_stress.level / 10 if latest_stress else 0  # Нормализуем до 0-10
        stress_points = stress_level  # Баллы собственной оценки стресса
        
        # Получаем данные о сне для указанной даты
        latest_sleep = SleepRecord.objects.filter(
            user=user,
            date__lte=date
        ).order_by('-date').first()
        
        sleep_hours = latest_sleep.duration_hours if latest_sleep else 8
        sleep_quality = latest_sleep.quality if latest_sleep and latest_sleep.quality else 7
        
        sleep_quality_points = 10 - sleep_quality  # Баллы качества сна
        sleep_deprivation_points = min((8 - sleep_hours) * 0.4, 10)  # Баллы недосыпа
        
        # Рассчитываем итоговый риск выгорания с учетом весов
        risk_factors = {
            'overtime': {
                'value': overtime_points,
                'weight': 0.15
            },
            'workday_duration': {
                'value': workday_duration_points,
                'weight': 0.10
            },
            'stress': {
                'value': stress_points,
                'weight': 0.20
            },
            'sleep_quality': {
                'value': sleep_quality_points,
                'weight': 0.20
            },
            'sleep_deprivation': {
                'value': sleep_deprivation_points,
                'weight': 0.20
            }
        }
        
        # Вычисляем итоговую оценку риска
        total_risk = (
            overtime_points * 0.15 +
            workday_duration_points * 0.10 +
            stress_points * 0.20 +
            sleep_quality_points * 0.20 +
            sleep_deprivation_points * 0.20
        )
        
        # Нормализуем до 0-100
        risk_level = min(max(total_risk * 10, 0), 100)
        
        # Формируем рекомендации на основе факторов риска
        recommendations = []
        
        if overtime_points > 2 or workday_duration_points > 2:
            recommendations.append({
                'type': 'work',
                'title': 'Сокращение рабочего времени',
                'description': 'Постарайтесь ограничить рабочее время до 8 часов в день, делегируйте задачи, если возможно.'
            })
            
        if stress_points > 5:
            recommendations.append({
                'type': 'stress',
                'title': 'Снижение уровня стресса',
                'description': 'Рекомендуется практиковать техники релаксации и медитации для снижения уровня стресса.'
            })
            
        if sleep_quality_points > 5:
            recommendations.append({
                'type': 'sleep',
                'title': 'Улучшение качества сна',
                'description': 'Создайте комфортные условия для сна: тихая комната, удобная кровать, отсутствие яркого света.'
            })
            
        if sleep_deprivation_points > 3:
            recommendations.append({
                'type': 'sleep',
                'title': 'Увеличение продолжительности сна',
                'description': 'Старайтесь спать не менее 7-8 часов в сутки для полноценного отдыха.'
            })
        
        return {
            'date': date,
            'risk_level': risk_level,
            'factors': risk_factors,
            'recommendations': recommendations,
            'raw_data': {
                'work_hours': work_hours,
                'stress_level': latest_stress.level if latest_stress else None,
                'sleep_hours': sleep_hours,
                'sleep_quality': sleep_quality
            }
        }
    
    @action(detail=False, methods=['get'])
    def calculate(self, request):
        """
        Рассчитывает текущий риск выгорания для пользователя динамически, без сохранения в базу данных.
        """
        user = request.user
        
        # Рассчитываем текущий риск выгорания без сохранения в БД
        burnout_data = self._calculate_burnout_risk(user)
        
        return Response(burnout_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        Возвращает текущую оценку риска выгорания, рассчитанную динамически.
        """
        user = request.user
        
        # Рассчитываем текущий риск выгорания без сохранения в БД
        burnout_data = self._calculate_burnout_risk(user)
        
        return Response(burnout_data)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Возвращает историю оценок риска выгорания за последние 7 дней.
        Данные рассчитываются динамически для каждого дня.
        """
        user = request.user
        now = timezone.now().date()
        week_ago = now - timedelta(days=7)
        
        # Получаем даты за последнюю неделю
        dates = [(week_ago + timedelta(days=i)) for i in range(8)]  # 8 дней, включая текущий
        
        # Создаем список объектов BurnoutRisk на основе рассчитанных данных
        burnout_risks = []
        for date in dates:
            if date <= now:  # Исключаем будущие даты
                risk_data = self._calculate_burnout_risk(user, date)
                
                # Создаем временный объект BurnoutRisk для сериализации
                # Мы не сохраняем его в базу данных, он используется только для формирования ответа
                burnout_risk = BurnoutRisk(
                    user=user,
                    risk_level=risk_data['risk_level'],
                    factors=risk_data['factors'],
                    recommendations=risk_data['recommendations']
                )
                
                # Устанавливаем дату и created_at для правильного отображения
                burnout_risk.date = date
                burnout_risk.created_at = timezone.make_aware(datetime.combine(date, datetime.min.time()))
                
                burnout_risks.append(burnout_risk)
        
        # Сериализуем данные с использованием стандартного сериализатора
        serializer = self.get_serializer(burnout_risks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def weekly_data(self, request):
        """
        Возвращает динамически рассчитанные данные о риске выгорания за последнюю неделю для построения графика.
        Не использует сохраненные данные из БД.
        """
        user = request.user
        now = timezone.now().date()
        week_ago = now - timedelta(days=7)
        
        # Получаем даты за последнюю неделю
        dates = [(week_ago + timedelta(days=i)) for i in range(8)]  # 8 дней, включая текущий
        
        # Создаем список объектов BurnoutRisk на основе рассчитанных данных
        burnout_risks = []
        chart_data = []
        
        for date in dates:
            if date <= now:  # Исключаем будущие даты
                risk_data = self._calculate_burnout_risk(user, date)
                
                # Создаем объект для chart_data
                chart_item = {
                    'date': date.strftime('%Y-%m-%d'),
                    'risk_level': risk_data['risk_level'],
                    'factors': {
                        'overtime': risk_data['factors']['overtime']['value'],
                        'workday_duration': risk_data['factors']['workday_duration']['value'],
                        'stress': risk_data['factors']['stress']['value'],
                        'sleep_quality': risk_data['factors']['sleep_quality']['value'],
                        'sleep_deprivation': risk_data['factors']['sleep_deprivation']['value']
                    }
                }
                chart_data.append(chart_item)
                
                # Создаем временный объект BurnoutRisk для сериализации
                burnout_risk = BurnoutRisk(
                    user=user,
                    risk_level=risk_data['risk_level'],
                    factors=risk_data['factors'],
                    recommendations=risk_data['recommendations']
                )
                
                # Устанавливаем дату и created_at для правильного отображения
                burnout_risk.date = date
                burnout_risk.created_at = timezone.make_aware(datetime.combine(date, datetime.min.time()))
                
                burnout_risks.append(burnout_risk)
        
        # Сериализуем историю рисков
        risk_serializer = self.get_serializer(burnout_risks, many=True)
        
        # Формируем итоговый ответ с данными для графика и весами факторов
        result = {
            'history': risk_serializer.data,
            'chart_data': chart_data,
            'factors_weights': {
                'overtime': 0.15,
                'workday_duration': 0.10,
                'stress': 0.20,
                'sleep_quality': 0.20,
                'sleep_deprivation': 0.20
            }
        }
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def calculate_factor_data(self, request):
        """
        Рассчитывает и возвращает данные по каждому фактору риска выгорания.
        Не сохраняет данные в БД.
        """
        user = request.user
        
        # Используем общий метод для расчета риска выгорания
        burnout_data = self._calculate_burnout_risk(user)
        
        return Response({
            'risk_level': burnout_data['risk_level'],
            'factor_data': burnout_data['factors'],
            'raw_data': burnout_data['raw_data']
        }) 