from django.db.models import Avg, Count, F
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import viewsets, permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from burnout_prevention.analytics.models import WorkActivity
from ..serializers.work_serializers import (
    WorkActivitySerializer, 
    WorkActivityCreateSerializer,
    WorkStatisticsSerializer,
    DailyWorkDataSerializer
)


class WorkActivityViewSet(viewsets.ModelViewSet):
    """
    API для управления записями о рабочей активности пользователя.
    
    Предоставляет функционал для создания, просмотра, обновления и удаления
    записей о продолжительности работы, перерывах и продуктивности.
    Также включает методы для получения статистики.
    """
    queryset = WorkActivity.objects.all()
    serializer_class = WorkActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date']
    
    @swagger_auto_schema(
        operation_description="Получить список записей о рабочей активности пользователя",
        responses={200: WorkActivitySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """
        Получение списка записей о рабочей активности текущего пользователя.
        
        Результаты можно фильтровать по дате используя параметр запроса 'date'.
        Формат даты: YYYY-MM-DD.
        """
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Создать новую запись о рабочей активности",
        request_body=WorkActivityCreateSerializer,
        responses={
            201: WorkActivitySerializer,
            400: "Неверные данные"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Создание новой записи о рабочей активности.
        
        Запись будет автоматически привязана к текущему пользователю.
        """
        return super().create(request, *args, **kwargs)
        
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
            return WorkActivityCreateSerializer
        return self.serializer_class
        
    @swagger_auto_schema(
        operation_description="Получить статистику рабочей активности за период",
        manual_parameters=[
            openapi.Parameter(
                'start_date',
                openapi.IN_QUERY,
                description="Начальная дата (формат: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'end_date',
                openapi.IN_QUERY,
                description="Конечная дата (формат: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
        ],
        responses={
            200: openapi.Response(
                description="Статистика рабочей активности",
                schema=WorkStatisticsSerializer
            ),
            400: "Неверный формат даты"
        }
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Возвращает статистику рабочей активности за указанный период.
        
        Позволяет получить агрегированные данные о рабочей активности,
        включая среднюю продолжительность работы, количество перерывов,
        общую продуктивность и детальную статистику по дням.
        
        Если параметры дат не указаны, возвращает статистику за последние 30 дней.
        
        Возвращаемые данные включают:
        - average_duration: Средняя продолжительность работы в часах
        - average_productivity: Средняя продуктивность (0-10)
        - average_breaks_count: Среднее количество перерывов
        - average_breaks_duration: Средняя продолжительность перерывов в минутах
        - total_records: Общее количество записей
        - start_date: Начальная дата периода в формате YYYY-MM-DD
        - end_date: Конечная дата периода в формате YYYY-MM-DD
        - daily_data: Ежедневные данные о работе с датой, продолжительностью, продуктивностью и заметками
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
            
        user_work_activities = WorkActivity.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Средние показатели работы
        aggregation = user_work_activities.aggregate(
            avg_duration=Avg('duration_hours'),
            avg_breaks=Avg('breaks_count'),
            avg_breaks_duration=Avg('breaks_total_minutes'),
            avg_productivity=Avg('productivity')
        )
        
        avg_duration = aggregation['avg_duration'] or 0
        avg_breaks = aggregation['avg_breaks'] or 0
        avg_breaks_duration = aggregation['avg_breaks_duration'] or 0
        avg_productivity = aggregation['avg_productivity'] or 0
        
        # Статистика по дням
        daily_data = [
            {
                'date': activity.date.strftime('%Y-%m-%d'),
                'duration_hours': activity.duration_hours,
                'productivity': activity.productivity,
                'notes': activity.notes
            }
            for activity in user_work_activities.order_by('date')
        ]
        
        data = {
            'average_duration': avg_duration,
            'average_breaks_count': avg_breaks,
            'average_breaks_duration': avg_breaks_duration,
            'average_productivity': avg_productivity,
            'total_records': user_work_activities.count(),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'daily_data': daily_data
        }
        
        serializer = WorkStatisticsSerializer(data)
        return Response(serializer.data)


class WorkStatisticsView(views.APIView):
    """
    API для получения статистики рабочей активности.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Получить статистику рабочей активности за указанный период",
        manual_parameters=[
            openapi.Parameter(
                'start_date',
                openapi.IN_QUERY,
                description="Начальная дата (формат: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'end_date',
                openapi.IN_QUERY,
                description="Конечная дата (формат: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
        ],
        responses={
            200: openapi.Response(
                description="Статистика рабочей активности",
                schema=WorkStatisticsSerializer
            ),
            400: "Неверный формат даты"
        }
    )
    def get(self, request):
        """
        Возвращает статистику рабочей активности за указанный период.
        
        Предоставляет детальную информацию о работе пользователя,
        включая продолжительность, количество перерывов и
        оценку продуктивности за каждый день в выбранном диапазоне.
        
        Возвращаемые данные включают:
        - average_duration: Средняя продолжительность работы в часах
        - average_productivity: Средняя продуктивность (0-10)
        - average_breaks_count: Среднее количество перерывов
        - average_breaks_duration: Средняя продолжительность перерывов в минутах
        - total_records: Общее количество записей
        - start_date: Начальная дата периода в формате YYYY-MM-DD
        - end_date: Конечная дата периода в формате YYYY-MM-DD
        - daily_data: Ежедневные данные о работе с датой, продолжительностью, продуктивностью и заметками
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
            
        user_work_activities = WorkActivity.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Средние показатели работы
        aggregation = user_work_activities.aggregate(
            avg_duration=Avg('duration_hours'),
            avg_breaks=Avg('breaks_count'),
            avg_breaks_duration=Avg('breaks_total_minutes'),
            avg_productivity=Avg('productivity')
        )
        
        avg_duration = aggregation['avg_duration'] or 0
        avg_breaks = aggregation['avg_breaks'] or 0
        avg_breaks_duration = aggregation['avg_breaks_duration'] or 0
        avg_productivity = aggregation['avg_productivity'] or 0
        
        # Статистика по дням
        daily_data = [
            {
                'date': activity.date.strftime('%Y-%m-%d'),
                'duration_hours': activity.duration_hours,
                'productivity': activity.productivity,
                'notes': activity.notes
            }
            for activity in user_work_activities.order_by('date')
        ]
        
        data = {
            'average_duration': avg_duration,
            'average_breaks_count': avg_breaks,
            'average_breaks_duration': avg_breaks_duration,
            'average_productivity': avg_productivity,
            'total_records': user_work_activities.count(),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'daily_data': daily_data
        }
        
        serializer = WorkStatisticsSerializer(data)
        return Response(serializer.data) 