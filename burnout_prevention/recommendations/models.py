from django.db import models
from django.utils.translation import gettext_lazy as _
from burnout_prevention.users.models import User


class RecommendationType(models.Model):
    """
    Типы рекомендаций для предотвращения выгорания.
    """
    name = models.CharField(_('название'), max_length=100)
    description = models.TextField(_('описание'))
    icon = models.CharField(_('иконка'), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('тип рекомендации')
        verbose_name_plural = _('типы рекомендаций')
        
    def __str__(self):
        return self.name


class Recommendation(models.Model):
    """
    Конкретные рекомендации для предотвращения выгорания.
    """
    type = models.ForeignKey(
        RecommendationType, 
        on_delete=models.CASCADE, 
        related_name='recommendations',
        verbose_name=_('тип')
    )
    title = models.CharField(_('заголовок'), max_length=200)
    description = models.TextField(_('описание'))
    duration_minutes = models.IntegerField(_('продолжительность (минуты)'), default=15)
    
    # Категории рекомендаций
    CATEGORY_CHOICES = [
        ('rest', _('Отдых')),
        ('sleep', _('Сон')),
        ('exercise', _('Физическая активность')),
        ('mindfulness', _('Осознанность')),
        ('social', _('Социальная активность')),
        ('work_balance', _('Баланс работы')),
    ]
    
    category = models.CharField(
        _('категория'), 
        max_length=50, 
        choices=CATEGORY_CHOICES,
        default='rest'
    )
    
    is_quick = models.BooleanField(
        _('быстрая рекомендация'), 
        default=False,
        help_text=_('Может быть выполнена быстро, например, в перерыве между работой')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('рекомендация')
        verbose_name_plural = _('рекомендации')
    
    def __str__(self):
        return self.title


class UserRecommendation(models.Model):
    """
    Рекомендации, предложенные конкретному пользователю.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='recommendations',
        verbose_name=_('пользователь')
    )
    recommendation = models.ForeignKey(
        Recommendation, 
        on_delete=models.CASCADE,
        verbose_name=_('рекомендация')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Статус рекомендации
    STATUS_CHOICES = [
        ('pending', _('В ожидании')),
        ('accepted', _('Принята')),
        ('completed', _('Выполнена')),
        ('rejected', _('Отклонена')),
    ]
    
    status = models.CharField(
        _('статус'), 
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Причина, по которой была создана рекомендация
    reason = models.TextField(_('причина'), blank=True)
    
    # Обратная связь от пользователя
    user_feedback = models.TextField(_('отзыв пользователя'), blank=True)
    user_rating = models.IntegerField(
        _('оценка пользователя'), 
        null=True, 
        blank=True,
        help_text=_('Оценка от 1 до 5')
    )
    
    completed_at = models.DateTimeField(_('дата выполнения'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('рекомендация пользователя')
        verbose_name_plural = _('рекомендации пользователей')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.email} - {self.recommendation.title} ({self.get_status_display()})" 