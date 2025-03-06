from django.db.models import Avg, Count, F
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import viewsets, permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from burnout_prevention.analytics.models import SleepRecord
from ..serializers.sleep_serializers import (
    SleepRecordSerializer, 
    SleepRecordCreateSerializer,
    SleepStatisticsSerializer
)


class SleepRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet для просмотра и редактирования записей о сне.
    """
    queryset = SleepRecord.objects.all()
    serializer_class = SleepRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date']
    
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
            return SleepRecordCreateSerializer
        return self.serializer_class
        
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Возвращает статистику сна за указанный период.
        """
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else (timezone.now().date() - timedelta(days=30))
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user_sleep_records = SleepRecord.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Средние показатели сна
        aggregation = user_sleep_records.aggregate(
            avg_duration=Avg('duration_hours'),
            avg_quality=Avg('quality')
        )
        
        avg_duration = aggregation['avg_duration'] or 0
        avg_quality = aggregation['avg_quality'] or 0
        
        # Статистика по дням
        statistics = [
            {
                'date': record.date.strftime('%Y-%m-%d'),
                'duration_hours': record.duration_hours,
                'quality': record.quality
            }
            for record in user_sleep_records.order_by('date')
        ]
        
        data = {
            'avg_duration': avg_duration,
            'avg_quality': avg_quality,
            'total_records': user_sleep_records.count(),
            'statistics': statistics
        }
        
        serializer = SleepStatisticsSerializer(data)
        return Response(serializer.data)


class SleepStatisticsView(views.APIView):
    """
    API для получения статистики сна.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Возвращает статистику сна за указанный период.
        """
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else (timezone.now().date() - timedelta(days=30))
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user_sleep_records = SleepRecord.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Средние показатели сна
        aggregation = user_sleep_records.aggregate(
            avg_duration=Avg('duration_hours'),
            avg_quality=Avg('quality')
        )
        
        avg_duration = aggregation['avg_duration'] or 0
        avg_quality = aggregation['avg_quality'] or 0
        
        # Статистика по дням
        statistics = [
            {
                'date': record.date.strftime('%Y-%m-%d'),
                'duration_hours': record.duration_hours,
                'quality': record.quality
            }
            for record in user_sleep_records.order_by('date')
        ]
        
        data = {
            'avg_duration': avg_duration,
            'avg_quality': avg_quality,
            'total_records': user_sleep_records.count(),
            'statistics': statistics
        }
        
        serializer = SleepStatisticsSerializer(data)
        return Response(serializer.data) 