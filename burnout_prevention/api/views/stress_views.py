from django.db.models import Avg, Count, F, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import viewsets, permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from burnout_prevention.analytics.models import StressLevel
from ..serializers.stress_serializers import (
    StressLevelSerializer, 
    StressLevelCreateSerializer,
    StressStatisticsSerializer
)


class StressLevelViewSet(viewsets.ModelViewSet):
    """
    ViewSet для просмотра и редактирования записей об уровне стресса.
    """
    queryset = StressLevel.objects.all()
    serializer_class = StressLevelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['created_at']
    
    def get_queryset(self):
        """
        Возвращает только записи текущего пользователя.
        """
        return self.queryset.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор.
        """
        if self.action == 'create':
            return StressLevelCreateSerializer
        return self.serializer_class
        
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Возвращает статистику уровня стресса за указанный период.
        """
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else (timezone.now().date() - timedelta(days=7))
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user_stress_levels = StressLevel.objects.filter(
            user=request.user,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        # Средний уровень стресса
        avg_level = user_stress_levels.aggregate(avg_level=Avg('level'))['avg_level'] or 0
        
        # Максимальный и минимальный уровень стресса
        max_level = user_stress_levels.aggregate(max_level=Max('level'))['max_level'] or 0
        min_level = user_stress_levels.aggregate(min_level=Min('level'))['min_level'] or 0
        
        # Расчет тренда (сравнение с предыдущим периодом такой же длительности)
        previous_start_date = start_date - (end_date - start_date)
        previous_end_date = start_date - timedelta(days=1)
        
        previous_period_levels = StressLevel.objects.filter(
            user=request.user,
            created_at__date__gte=previous_start_date,
            created_at__date__lte=previous_end_date
        )
        
        previous_avg_level = previous_period_levels.aggregate(avg_level=Avg('level'))['avg_level'] or 0
        trend_value = avg_level - previous_avg_level
        trend_direction = 'stable'
        if trend_value > 0:
            trend_direction = 'up'
        elif trend_value < 0:
            trend_direction = 'down'
        
        # Статистика по дням
        daily_stats = user_stress_levels.values('created_at__date').annotate(
            date=F('created_at__date'),
            avg_level=Avg('level'),
            count=Count('id')
        ).order_by('created_at__date')
        
        statistics = [
            {
                'date': stat['date'].strftime('%Y-%m-%d'),
                'avg_level': stat['avg_level'],
                'count': stat['count']
            }
            for stat in daily_stats
        ]
        
        data = {
            'avg_level': avg_level,
            'max_level': max_level,
            'min_level': min_level,
            'total_records': user_stress_levels.count(),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'trend': {
                'value': trend_value,
                'direction': trend_direction
            },
            'statistics': statistics
        }
        
        serializer = StressStatisticsSerializer(data)
        return Response(serializer.data)


class StressStatisticsView(views.APIView):
    """
    API для получения статистики уровня стресса.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Возвращает статистику уровня стресса за указанный период.
        """
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else (timezone.now().date() - timedelta(days=7))
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user_stress_levels = StressLevel.objects.filter(
            user=request.user,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        # Средний уровень стресса
        avg_level = user_stress_levels.aggregate(avg_level=Avg('level'))['avg_level'] or 0
        
        # Максимальный и минимальный уровень стресса
        max_level = user_stress_levels.aggregate(max_level=Max('level'))['max_level'] or 0
        min_level = user_stress_levels.aggregate(min_level=Min('level'))['min_level'] or 0
        
        # Расчет тренда (сравнение с предыдущим периодом такой же длительности)
        previous_start_date = start_date - (end_date - start_date)
        previous_end_date = start_date - timedelta(days=1)
        
        previous_period_levels = StressLevel.objects.filter(
            user=request.user,
            created_at__date__gte=previous_start_date,
            created_at__date__lte=previous_end_date
        )
        
        previous_avg_level = previous_period_levels.aggregate(avg_level=Avg('level'))['avg_level'] or 0
        trend_value = avg_level - previous_avg_level
        trend_direction = 'stable'
        if trend_value > 0:
            trend_direction = 'up'
        elif trend_value < 0:
            trend_direction = 'down'
        
        # Статистика по дням
        daily_stats = user_stress_levels.values('created_at__date').annotate(
            date=F('created_at__date'),
            avg_level=Avg('level'),
            count=Count('id')
        ).order_by('created_at__date')
        
        statistics = [
            {
                'date': stat['date'].strftime('%Y-%m-%d'),
                'avg_level': stat['avg_level'],
                'count': stat['count']
            }
            for stat in daily_stats
        ]
        
        data = {
            'avg_level': avg_level,
            'max_level': max_level,
            'min_level': min_level,
            'total_records': user_stress_levels.count(),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'trend': {
                'value': trend_value,
                'direction': trend_direction
            },
            'statistics': statistics
        }
        
        serializer = StressStatisticsSerializer(data)
        return Response(serializer.data) 