from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Burnout Prevention API",
        default_version="v1",
        description="""
        API для рекомендательной системы по предотвращению выгорания
        
        ## Основные возможности API
        
        * **Пользователи**: регистрация, авторизация, управление профилями
        * **Стресс**: отслеживание уровня стресса и анализ динамики
        * **Сон**: мониторинг качества и продолжительности сна
        * **Работа**: анализ рабочей активности и продуктивности
        * **Рекомендации**: персонализированные рекомендации по предотвращению выгорания
        * **Интеграции**: подключение внешних сервисов и календарей
        
        Для использования API требуется авторизация через JWT токены.
        """,
        terms_of_service="https://burnout-prevention.ru/terms/",
        contact=openapi.Contact(email="info@burnout-prevention.ru"),
        license=openapi.License(name="Proprietary License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('burnout_prevention.api.urls')),
    
    # Документация API
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/docs/json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 