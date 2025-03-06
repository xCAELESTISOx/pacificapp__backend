from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Расширенная модель пользователя для системы предотвращения выгорания.
    """
    email = models.EmailField(_('email address'), unique=True)
    
    # Дополнительная информация о пользователе
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    # Метаданные для анализа выгорания
    stress_level_base = models.IntegerField(
        _('базовый уровень стресса'), 
        default=50,
        help_text=_('Базовый уровень стресса от 0 до 100')
    )
    sleep_hours_avg = models.FloatField(
        _('среднее время сна (часов)'), 
        null=True, 
        blank=True
    )
    work_hours_daily = models.FloatField(
        _('среднее рабочее время (часов в день)'), 
        null=True, 
        blank=True
    )
    
    # Настройки уведомлений
    notifications_enabled = models.BooleanField(default=True)
    notification_frequency = models.IntegerField(
        _('частота уведомлений (минуты)'),
        default=60
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        
    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """
    Расширенный профиль пользователя с дополнительными настройками.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Предпочтения для отдыха и релаксации
    RELAXATION_CHOICES = [
        ('meditation', _('Медитация')),
        ('exercise', _('Физические упражнения')),
        ('reading', _('Чтение')),
        ('music', _('Музыка')),
        ('walking', _('Прогулка')),
        ('art', _('Творчество')),
        ('social', _('Общение')),
    ]
    
    preferred_relaxation_methods = models.JSONField(
        _('предпочитаемые методы релаксации'),
        default=list,
        help_text=_('Список предпочитаемых методов релаксации')
    )
    
    work_start_time = models.TimeField(_('время начала работы'), null=True, blank=True)
    work_end_time = models.TimeField(_('время окончания работы'), null=True, blank=True)
    
    # Интеграции с внешними сервисами
    google_calendar_connected = models.BooleanField(default=False)
    outlook_connected = models.BooleanField(default=False)
    
    # Метаданные профиля
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
        
    def __str__(self):
        return f"Профиль {self.user.email}"


class UserActivity(models.Model):
    """
    Модель для хранения истории активности пользователя.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    
    ACTIVITY_TYPES = [
        ('login', _('Вход в систему')),
        ('logout', _('Выход из системы')),
        ('profile_update', _('Обновление профиля')),
        ('recommendation_view', _('Просмотр рекомендации')),
        ('exercise_complete', _('Завершение упражнения')),
        ('survey_complete', _('Завершение опроса')),
        ('settings_change', _('Изменение настроек')),
        ('other', _('Другое')),
    ]
    
    activity_type = models.CharField(
        _('тип активности'),
        max_length=50,
        choices=ACTIVITY_TYPES
    )
    
    description = models.TextField(_('описание'), blank=True)
    timestamp = models.DateTimeField(_('время'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('user activity')
        verbose_name_plural = _('user activities')
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.timestamp}" 