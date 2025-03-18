from django.db import models
from django.utils.translation import gettext_lazy as _
from burnout_prevention.users.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class StressLevel(models.Model):
    """
    Модель для отслеживания уровня стресса пользователя.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='stress_level_records',  # Changed to a unique related_name
        verbose_name=_('пользователь')
    )
    
    level = models.IntegerField(
        _('уровень стресса'), 
        help_text=_('Уровень стресса от 0 до 100')
    )
    
    notes = models.TextField(_('заметки'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('уровень стресса')
        verbose_name_plural = _('уровни стресса')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.email} - {self.level} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"


class SleepRecord(models.Model):
    """
    Запись о сне пользователя.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sleep_records',
        verbose_name=_('пользователь')
    )
    
    date = models.DateField(_('дата'))
    duration_hours = models.FloatField(_('продолжительность (часов)'))
    quality = models.IntegerField(
        _('качество сна'), 
        help_text=_('Оценка качества сна от 1 до 10'),
        null=True, 
        blank=True
    )
    
    notes = models.TextField(_('заметки'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('запись о сне')
        verbose_name_plural = _('записи о сне')
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.user.email} - {self.duration_hours} ч ({self.date})"


class WorkActivity(models.Model):
    """
    Запись о рабочей активности пользователя.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='work_activities',
        verbose_name=_('пользователь')
    )
    
    date = models.DateField(_('дата'))
    duration_hours = models.FloatField(_('продолжительность (часов)'))
    breaks_count = models.IntegerField(_('количество перерывов'), default=0)
    breaks_total_minutes = models.IntegerField(_('общая продолжительность перерывов (минуты)'), default=0)
    
    productivity = models.IntegerField(
        _('продуктивность'), 
        help_text=_('Оценка продуктивности от 1 до 10'),
        null=True, 
        blank=True
    )
    
    notes = models.TextField(_('заметки'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('рабочая активность')
        verbose_name_plural = _('рабочие активности')
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.user.email} - {self.duration_hours} ч ({self.date})"


class BurnoutRisk(models.Model):
    """
    Модель для отслеживания риска выгорания пользователя
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='burnout_risks')
    date = models.DateField(auto_now_add=True)
    risk_level = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Уровень риска выгорания (0-100)"
    )
    factors = models.JSONField(default=dict, blank=True, null=True,
                              help_text="Факторы риска выгорания и их значения")
    recommendations = models.JSONField(default=list, blank=True, null=True,
                                     help_text="Рекомендации по предотвращению выгорания")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.risk_level}% ({self.created_at.strftime('%Y-%m-%d')})"
