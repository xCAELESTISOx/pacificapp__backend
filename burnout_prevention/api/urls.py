from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserViewSet,
    StressLevelViewSet, StressStatisticsView,
    SleepRecordViewSet, SleepStatisticsView,
    WorkActivityViewSet, WorkStatisticsView,
    RecommendationViewSet, UserRecommendationViewSet,
    BurnoutRiskViewSet,
    CalendarIntegrationViewSet,
    DashboardView
)

# Создаем роутер для ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'stress', StressLevelViewSet, basename='stress')
router.register(r'sleep', SleepRecordViewSet, basename='sleep')
router.register(r'work-activity', WorkActivityViewSet, basename='work-activity')
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')
router.register(r'user-recommendations', UserRecommendationViewSet, basename='user-recommendation')
router.register(r'burnout-risk', BurnoutRiskViewSet, basename='burnout-risk')
router.register(r'calendar', CalendarIntegrationViewSet, basename='calendar')

urlpatterns = [
    # Авторизация и JWT токены (исправлено в соответствии с YAML-схемой)
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Включаем URL-адреса, сгенерированные роутером
    path('', include(router.urls)),
    
    # Дополнительные URL-адреса для представлений, не являющихся ViewSets
    path('stress/statistics/', StressStatisticsView.as_view(), name='stress-statistics'),
    path('sleep/statistics/', SleepStatisticsView.as_view(), name='sleep-statistics'),
    path('work-activity/statistics/', WorkStatisticsView.as_view(), name='work-statistics'),
    path('dashboard/summary/', DashboardView.as_view(), name='dashboard'),  # Исправлено в соответствии с YAML-схемой
    
    # URL для аутентификации
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
] 