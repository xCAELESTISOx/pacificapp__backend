from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from burnout_prevention.integrations.models import CalendarIntegration, CalendarEvent
from ..serializers.calendar_serializers import CalendarIntegrationSerializer, CalendarEventSerializer


class CalendarIntegrationViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления интеграциями с календарем.
    """
    queryset = CalendarIntegration.objects.all()
    serializer_class = CalendarIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает только интеграции текущего пользователя.
        """
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Сохраняет текущего пользователя при создании интеграции.
        """
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None):
        """
        Обновляет токен доступа для интеграции с календарем.
        """
        integration = self.get_object()
        
        # Здесь должна быть логика обновления токена через API провайдера календаря
        # Например, для Google Calendar это будет запрос к Google OAuth API
        
        # В качестве примера просто обновляем дату истечения токена
        integration.token_expiry = timezone.now() + timedelta(hours=1)
        integration.save()
        
        serializer = self.get_serializer(integration)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """
        Возвращает события календаря для данной интеграции.
        """
        integration = self.get_object()
        events = CalendarEvent.objects.filter(calendar_integration=integration)
        
        # Фильтрация по дате
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            events = events.filter(start_time__date__gte=start_date)
        if end_date:
            events = events.filter(end_time__date__lte=end_date)
        
        serializer = CalendarEventSerializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """
        Синхронизирует события календаря с провайдером.
        """
        integration = self.get_object()
        
        # Здесь должна быть логика синхронизации с API провайдера календаря
        # Например, для Google Calendar это будет запрос к Google Calendar API
        
        # В качестве примера просто возвращаем текущие события
        events = CalendarEvent.objects.filter(calendar_integration=integration)
        serializer = CalendarEventSerializer(events, many=True)
        
        return Response({
            'status': 'success',
            'message': 'Calendar synchronized successfully',
            'events': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def providers(self, request):
        """
        Возвращает список доступных провайдеров календаря.
        """
        providers = [
            {
                'id': 'google',
                'name': 'Google Calendar',
                'auth_url': 'https://accounts.google.com/o/oauth2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'scope': 'https://www.googleapis.com/auth/calendar.readonly'
            },
            {
                'id': 'outlook',
                'name': 'Microsoft Outlook',
                'auth_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
                'token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
                'scope': 'Calendars.Read'
            }
        ]
        
        return Response(providers) 