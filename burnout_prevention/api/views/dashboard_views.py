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
        
        # Получаем данные о риске выгорания
        burnout_risk_data = None
        burnout_risks = BurnoutRisk.objects.all()
        if user_is_authenticated:
            burnout_risks = burnout_risks.filter(user=user)
        else:
            burnout_risks = BurnoutRisk.objects.none()
            
        latest_burnout_risk = burnout_risks.order_by('-created_at').first()
        burnout_risk_current = 0
        burnout_risk_previous = 0
        burnout_risk_trend = 0
        
        if latest_burnout_risk:
            burnout_risk_current = latest_burnout_risk.risk_level
            
            prev_burnout_risk = burnout_risks.exclude(id=latest_burnout_risk.id).order_by('-created_at').first()
            burnout_risk_previous = prev_burnout_risk.risk_level if prev_burnout_risk else 0
            burnout_risk_trend = burnout_risk_current - burnout_risk_previous
            
            burnout_risk_data = {
                'current': burnout_risk_current,
                'previous': burnout_risk_previous,
                'trend': {
                    'value': burnout_risk_trend,
                    'direction': 'up' if burnout_risk_trend > 0 else ('down' if burnout_risk_trend < 0 else 'stable')
                }
            }
        # Если нет существующих данных о риске выгорания, пытаемся рассчитать динамически
        elif user_is_authenticated:
            # Проверяем наличие всех необходимых данных для расчета
            has_stress_data = latest_stress is not None
            has_sleep_data = latest_sleep is not None
            has_work_data = latest_work is not None
            
            # Рассчитываем риск выгорания только если есть все необходимые данные
            if has_stress_data and has_sleep_data and has_work_data:
                # Определяем вес каждого фактора в определении риска выгорания
                stress_weight = 0.4
                sleep_weight = 0.3
                work_weight = 0.3
                
                # Рассчитываем компоненты риска выгорания
                stress_risk = min(stress_level_current * 10, 100)
                
                # Инвертируем оценку сна (меньше сна = выше риск)
                sleep_risk = max(0, 100 - (sleep_duration_current * 10))
                
                # Риск по работе (длительная работа и низкая продуктивность увеличивают риск)
                work_duration_risk = min(work_duration_current * 5, 100)
                work_productivity_risk = max(0, 100 - (work_productivity_current * 10))
                work_risk = (work_duration_risk + work_productivity_risk) / 2
                
                # Общий риск выгорания
                burnout_risk_current = int(
                    stress_risk * stress_weight + 
                    sleep_risk * sleep_weight + 
                    work_risk * work_weight
                )
                
                # Создаем новую запись о риске выгорания
                new_risk = BurnoutRisk(
                    user=user,
                    risk_level=burnout_risk_current
                )
                new_risk.save()
                
                burnout_risk_data = {
                    'current': burnout_risk_current,
                    'trend': {
                        'value': burnout_risk_current,
                        'direction': 'up' if burnout_risk_current > 0 else 'stable'
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
                            }
                            for rec in latest_recs
                        ]
            except Exception:
                # В случае любой ошибки с БД, оставляем базовые значения
                pass
        
        # Формируем данные для панели мониторинга в соответствии с новой схемой
        dashboard_data = {
            # Новая структура в соответствии со схемой TS фронтенда
            'sleep': {
                'average_duration': sleep_duration_monthly_avg,
                'average_quality': sleep_quality_monthly_avg,
                'total_records': sleep_records.count(),
                'trend': {
                    'value': sleep_duration_trend,
                    'direction': 'up' if sleep_duration_trend > 0 else ('down' if sleep_duration_trend < 0 else 'stable')
                }
            },
            'stress': {
                'avg_level': stress_level_monthly_avg,
                'max_level': stress_records_month.aggregate(max_level=Max('level'))['max_level'] or 0,
                'min_level': stress_records_month.aggregate(min_level=Min('level'))['min_level'] or 0,
                'total_records': stress_records.count(),
                'start_date': month_ago.strftime('%Y-%m-%d'),
                'end_date': today.strftime('%Y-%m-%d'),
                'statistics': [
                    {
                        'date': day.strftime('%Y-%m-%d'),
                        'avg_level': stress_records.filter(
                            created_at__date=day
                        ).aggregate(avg_level=Avg('level'))['avg_level'] or 0,
                        'count': stress_records.filter(created_at__date=day).count()
                    }
                    for day in [(today - timedelta(days=i)) for i in range(30)]
                ],
                'trend': {
                    'value': stress_level_trend,
                    'direction': 'down' if stress_level_trend < 0 else ('up' if stress_level_trend > 0 else 'stable')
                }
            },
            'work': {
                'average_duration': work_duration_monthly_avg,
                'average_productivity': work_productivity_monthly_avg,
                'total_records': work_records.count(),
                'trend': {
                    'value': work_duration_trend,
                    'direction': 'up' if work_duration_trend > 0 else ('down' if work_duration_trend < 0 else 'stable')
                }
            },
            'recommendations': {
                'pending': pending_recommendations_count,
                'completed': completed_recommendations_count,
                'accepted': accepted_recommendations_count,
                'latest': latest_recommendations
            },
            'burnout_risk': burnout_risk_data
        }
        
        serializer = DashboardSerializer(dashboard_data)
        return Response(serializer.data) 