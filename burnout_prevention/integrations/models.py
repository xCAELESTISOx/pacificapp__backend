from django.db import models
from django.utils.translation import gettext_lazy as _
from burnout_prevention.users.models import User


class CalendarIntegration(models.Model):
    """
    Интеграция с календарями (Google Calendar, Outlook).
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='calendar_integrations',
        verbose_name=_('пользователь')
    )
    
    CALENDAR_TYPE_CHOICES = [
        ('google', 'Google Calendar'),
        ('outlook', 'Microsoft Outlook'),
    ]
    
    type = models.CharField(
        _('тип календаря'), 
        max_length=20, 
        choices=CALENDAR_TYPE_CHOICES
    )
    
    # Токены для доступа к API
    access_token = models.TextField(_('токен доступа'), blank=True)
    refresh_token = models.TextField(_('токен обновления'), blank=True)
    token_expiry = models.DateTimeField(_('срок действия токена'), null=True, blank=True)
    
    is_active = models.BooleanField(_('активна'), default=True)
    last_sync = models.DateTimeField(_('последняя синхронизация'), null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('интеграция с календарем')
        verbose_name_plural = _('интеграции с календарями')
        unique_together = ('user', 'type')
        
    def __str__(self):
        return f"{self.user.email} - {self.get_type_display()}"


class CalendarEvent(models.Model):
    """
    События из календаря пользователя.
    """
    integration = models.ForeignKey(
        CalendarIntegration, 
        on_delete=models.CASCADE, 
        related_name='events',
        verbose_name=_('интеграция')
    )
    
    event_id = models.CharField(_('ID события'), max_length=255)
    title = models.CharField(_('заголовок'), max_length=255)
    description = models.TextField(_('описание'), blank=True)
    
    start_time = models.DateTimeField(_('время начала'))
    end_time = models.DateTimeField(_('время окончания'))
    is_all_day = models.BooleanField(_('весь день'), default=False)
    
    location = models.CharField(_('место'), max_length=255, blank=True)
    
    # Метаданные для анализа выгорания
    is_meeting = models.BooleanField(_('встреча'), default=True)
    attendees_count = models.IntegerField(_('количество участников'), default=0)
    
    stress_score = models.IntegerField(
        _('оценка стресса'), 
        null=True, 
        blank=True,
        help_text=_('Оценка потенциального стресса от этого события (от 0 до 100)')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('событие календаря')
        verbose_name_plural = _('события календаря')
        unique_together = ('integration', 'event_id')
        ordering = ['-start_time']
        
    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%d.%m.%Y %H:%M')})"


class ComputerActivityLog(models.Model):
    """
    Логи активности пользователя за компьютером/в браузере.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='activity_logs',
        verbose_name=_('пользователь')
    )
    
    date = models.DateField(_('дата'))
    
    # Данные о активности
    active_hours = models.FloatField(_('активные часы'), default=0.0)
    total_keyboard_actions = models.IntegerField(_('всего действий клавиатуры'), default=0)
    total_mouse_actions = models.IntegerField(_('всего действий мыши'), default=0)
    
    # Данные о перерывах
    breaks_count = models.IntegerField(_('количество перерывов'), default=0)
    breaks_duration_minutes = models.IntegerField(_('продолжительность перерывов (минуты)'), default=0)
    
    # Метаданные о рабочем дне
    work_start_time = models.TimeField(_('время начала работы'), null=True, blank=True)
    work_end_time = models.TimeField(_('время окончания работы'), null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('лог активности компьютера')
        verbose_name_plural = _('логи активности компьютера')
        unique_together = ('user', 'date')
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.user.email} - {self.date} ({self.active_hours} ч)" 