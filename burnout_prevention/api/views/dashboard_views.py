from django.db.models import Avg, Count, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.db import connection

from burnout_prevention.analytics.models import (
    StressLevel, 
    SleepRecord, 
    WorkActivity, 
    BurnoutRisk
)
from burnout_prevention.recommendations.models import UserRecommendation
from ..serializers.dashboard_serializers import DashboardSerializer
from .burnout_views import BurnoutRiskViewSet


class DashboardView(views.APIView):
    """
    API для получения данных панели мониторинга.
    """
    # Возвращаем обратно требование аутентификации
    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = []
    
    def get(self, request):
        """
        Возвращает агрегированные данные для панели мониторинга.
        """
        user = request.user
        now = timezone.now()
        today = now.date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Проверяем, аутентифицирован ли пользователь
        user_is_authenticated = user.is_authenticated
        user_id = user.id if user_is_authenticated else None
        
        # Получаем данные о стрессе
        stress_records = StressLevel.objects.all()
        if user_is_authenticated:
            stress_records = stress_records.filter(user=user)
        else:
            stress_records = StressLevel.objects.none()
            
        stress_records_week = stress_records.filter(created_at__date__gte=week_ago) if user_is_authenticated else StressLevel.objects.none()
        stress_records_month = stress_records.filter(created_at__date__gte=month_ago) if user_is_authenticated else StressLevel.objects.none()
        
        latest_stress = stress_records.order_by('-created_at').first()
        stress_level_current = latest_stress.level if latest_stress else 0
        
        stress_level_weekly_avg = stress_records_week.aggregate(avg=Avg('level'))['avg'] or 0
        stress_level_monthly_avg = stress_records_month.aggregate(avg=Avg('level'))['avg'] or 0
        
        # Тренд стресса (сравнение текущей недели с предыдущей)
        prev_week_start = week_ago - timedelta(days=7)
        prev_week_stress = 0
        if user_is_authenticated:
            prev_week_stress = stress_records.filter(
                created_at__date__gte=prev_week_start,
                created_at__date__lt=week_ago
            ).aggregate(avg=Avg('level'))['avg'] or 0
        
        stress_level_trend = stress_level_weekly_avg - prev_week_stress
        
        # Получаем данные о сне
        sleep_records = SleepRecord.objects.all()
        if user_is_authenticated:
            sleep_records = sleep_records.filter(user=user)
        else:
            sleep_records = SleepRecord.objects.none()
            
        sleep_records_week = sleep_records.filter(date__gte=week_ago) if user_is_authenticated else SleepRecord.objects.none()
        sleep_records_month = sleep_records.filter(date__gte=month_ago) if user_is_authenticated else SleepRecord.objects.none()
        
        latest_sleep = sleep_records.order_by('-date').first()
        sleep_duration_current = latest_sleep.duration_hours if latest_sleep else 0
        sleep_quality_current = latest_sleep.quality if latest_sleep else 0
        
        sleep_duration_weekly_avg = sleep_records_week.aggregate(avg=Avg('duration_hours'))['avg'] or 0
        sleep_duration_monthly_avg = sleep_records_month.aggregate(avg=Avg('duration_hours'))['avg'] or 0
        
        sleep_quality_weekly_avg = sleep_records_week.aggregate(avg=Avg('quality'))['avg'] or 0
        sleep_quality_monthly_avg = sleep_records_month.aggregate(avg=Avg('quality'))['avg'] or 0
        
        # Тренд сна
        prev_week_sleep_duration = 0
        if user_is_authenticated:
            prev_week_sleep_duration = sleep_records.filter(
                date__gte=prev_week_start,
                date__lt=week_ago
            ).aggregate(avg=Avg('duration_hours'))['avg'] or 0
        
        sleep_duration_trend = sleep_duration_weekly_avg - prev_week_sleep_duration
        
        # Получаем данные о работе
        work_records = WorkActivity.objects.all()
        if user_is_authenticated:
            work_records = work_records.filter(user=user)
        else:
            work_records = WorkActivity.objects.none()
            
        work_records_week = work_records.filter(date__gte=week_ago) if user_is_authenticated else WorkActivity.objects.none()
        work_records_month = work_records.filter(date__gte=month_ago) if user_is_authenticated else WorkActivity.objects.none()
        
        latest_work = work_records.order_by('-date').first()
        work_duration_current = latest_work.duration_hours if latest_work else 0
        work_productivity_current = latest_work.productivity if latest_work else 0
        
        work_duration_weekly_avg = work_records_week.aggregate(avg=Avg('duration_hours'))['avg'] or 0
        work_duration_monthly_avg = work_records_month.aggregate(avg=Avg('duration_hours'))['avg'] or 0
        
        work_productivity_weekly_avg = work_records_week.aggregate(avg=Avg('productivity'))['avg'] or 0
        work_productivity_monthly_avg = work_records_month.aggregate(avg=Avg('productivity'))['avg'] or 0
        
        # Тренд работы
        prev_week_work_duration = 0
        if user_is_authenticated:
            prev_week_work_duration = work_records.filter(
                date__gte=prev_week_start,
                date__lt=week_ago
            ).aggregate(avg=Avg('duration_hours'))['avg'] or 0
        
        work_duration_trend = work_duration_weekly_avg - prev_week_work_duration
        
        # Получаем данные о риске выгорания (динамический расчет)
        burnout_risk_data = None
        if user_is_authenticated:
            # Создаем экземпляр BurnoutRiskViewSet для использования его метода _calculate_burnout_risk
            burnout_risk_viewset = BurnoutRiskViewSet()
            
            # Рассчитываем текущий риск выгорания
            current_risk_data = burnout_risk_viewset._calculate_burnout_risk(user)
            current_risk_level = current_risk_data['risk_level']
            
            # Рассчитываем риск выгорания для предыдущего дня
            yesterday = today - timedelta(days=1)
            prev_risk_data = burnout_risk_viewset._calculate_burnout_risk(user, yesterday)
            prev_risk_level = prev_risk_data['risk_level']
            
            # Рассчитываем тренд
            burnout_risk_trend = current_risk_level - prev_risk_level
            
            burnout_risk_data = {
                'current': current_risk_level,
                'previous': prev_risk_level,
                'trend': {
                    'value': burnout_risk_trend,
                    'direction': 'up' if burnout_risk_trend > 0 else ('down' if burnout_risk_trend < 0 else 'stable')
                }
            }
        
        # Получаем данные о рекомендациях
        pending_recommendations_count = 0
        completed_recommendations_count = 0
        accepted_recommendations_count = 0
        latest_recommendations = []
        
        # Безопасная проверка наличия таблицы
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='recommendations_userrecommendation'"
                )
                table_exists = cursor.fetchone()[0] > 0
                
                if table_exists and user_is_authenticated:
                    cursor.execute(
                        "SELECT COUNT(*) FROM recommendations_userrecommendation WHERE user_id = ? AND status = 'pending'",
                        [user.id]
                    )
                    pending_recommendations_count = cursor.fetchone()[0]
                    
                    cursor.execute(
                        "SELECT COUNT(*) FROM recommendations_userrecommendation WHERE user_id = ? AND status = 'completed'",
                        [user.id]
                    )
                    completed_recommendations_count = cursor.fetchone()[0]
                    
                    cursor.execute(
                        "SELECT COUNT(*) FROM recommendations_userrecommendation WHERE user_id = ? AND status = 'accepted'",
                        [user.id]
                    )
                    accepted_recommendations_count = cursor.fetchone()[0]
                    
                    # Получаем последние рекомендации
                    cursor.execute(
                        """
                        SELECT id, title, category, status 
                        FROM recommendations_userrecommendation 
                        WHERE user_id = ? 
                        ORDER BY created_at DESC 
                        LIMIT 5
                        """,
                        [user.id]
                    )
                    latest_recs = cursor.fetchall()
                    if latest_recs:
                        latest_recommendations = [
                            {
                                'id': rec[0],
                                'title': rec[1],
                                'category': rec[2],
                                'status': rec[3]
                            } for rec in latest_recs
                        ]
            except Exception as e:
                # Просто пропускаем ошибки для безопасности
                pass
        
        # Формируем данные для панели мониторинга
        dashboard_data = {
            # Сон
            'sleep': {
                'average_duration': sleep_duration_weekly_avg,
                'average_quality': sleep_quality_weekly_avg,
                'total_records': sleep_records_week.count(),
                'trend': {
                    'value': sleep_duration_trend,
                    'direction': 'up' if sleep_duration_trend > 0 else ('down' if sleep_duration_trend < 0 else 'stable')
                }
            },
            # Стресс
            'stress': {
                'avg_level': stress_level_weekly_avg,
                'max_level': stress_records_week.aggregate(max=Max('level'))['max'] or 0,
                'min_level': stress_records_week.aggregate(min=Min('level'))['min'] or 0,
                'total_records': stress_records_week.count(),
                'start_date': week_ago.strftime('%Y-%m-%d'),
                'end_date': today.strftime('%Y-%m-%d'),
                'statistics': [], # Будет заполнено позже
                'trend': {
                    'value': stress_level_trend,
                    'direction': 'up' if stress_level_trend > 0 else ('down' if stress_level_trend < 0 else 'stable')
                }
            },
            # Работа
            'work': {
                'average_duration': work_duration_weekly_avg,
                'average_productivity': work_productivity_weekly_avg,
                'total_records': work_records_week.count(),
                'trend': {
                    'value': work_duration_trend,
                    'direction': 'up' if work_duration_trend > 0 else ('down' if work_duration_trend < 0 else 'stable')
                }
            },
            # Рекомендации
            'recommendations': {
                'pending': pending_recommendations_count,
                'completed': completed_recommendations_count,
                'accepted': accepted_recommendations_count,
                'latest': latest_recommendations
            },
            # Риск выгорания
            'burnout_risk': burnout_risk_data
        }
        
        # Форматируем статистику для стресса
        # Группируем данные по дням и рассчитываем средний стресс для каждого дня
        if user_is_authenticated:
            daily_stress = {}
            
            # Создаем словарь для хранения данных по дням
            date_range = [week_ago + timedelta(days=i) for i in range((today - week_ago).days + 1)]
            for date in date_range:
                date_str = date.strftime('%Y-%m-%d')
                daily_stress[date_str] = {
                    'date': date_str,
                    'level': 0,
                    'count': 0
                }
                
            # Заполняем данные по стрессу
            for record in stress_records_week:
                date_str = record.created_at.date().strftime('%Y-%m-%d')
                if date_str in daily_stress:
                    daily_stress[date_str]['level'] += record.level
                    daily_stress[date_str]['count'] += 1
                    
            # Рассчитываем средний стресс для каждого дня
            for date_str, data in daily_stress.items():
                if data['count'] > 0:
                    data['level'] = round(data['level'] / data['count'], 1)
                    
            # Сортируем по дате и добавляем в ответ
            dashboard_data['stress']['statistics'] = [
                data for _, data in sorted(daily_stress.items())
            ]
            
        serializer = DashboardSerializer(dashboard_data)
        return Response(serializer.data) 