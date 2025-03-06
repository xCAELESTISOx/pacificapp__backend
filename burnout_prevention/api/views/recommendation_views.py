from rest_framework import viewsets, permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from burnout_prevention.recommendations.models import Recommendation, UserRecommendation
from ..serializers.recommendation_serializers import (
    RecommendationSerializer,
    UserRecommendationSerializer,
    UserRecommendationUpdateSerializer
)


class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра всех рекомендаций.
    Только чтение, так как создание рекомендаций выполняется через админку или API рекомендательной системы.
    """
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_quick', 'type']


class UserRecommendationViewSet(viewsets.ModelViewSet):
    """
    ViewSet для просмотра и управления рекомендациями пользователя.
    """
    queryset = UserRecommendation.objects.all()
    serializer_class = UserRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'recommendation__category']
    
    def get_queryset(self):
        """
        Возвращает только рекомендации текущего пользователя.
        """
        return self.queryset.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия.
        """
        if self.action in ['update', 'partial_update']:
            return UserRecommendationUpdateSerializer
        return self.serializer_class
    
    @action(detail=False, methods=['post'])
    def request_new(self, request):
        """
        Запрашивает новые рекомендации для пользователя.
        Этот метод может вызывать рекомендательную систему или 
        выбирать рекомендации на основе текущих данных пользователя.
        """
        # Здесь должна быть логика для создания новых рекомендаций
        # Например, вызов рекомендательной системы или алгоритма
        
        # В качестве примера просто возьмем неназначенные пользователю рекомендации
        user = request.user
        existing_recommendations = UserRecommendation.objects.filter(
            user=user
        ).values_list('recommendation_id', flat=True)
        
        new_recommendations = Recommendation.objects.exclude(
            id__in=existing_recommendations
        )[:5]  # Ограничим до 5 новых рекомендаций
        
        created_recommendations = []
        for recommendation in new_recommendations:
            user_recommendation = UserRecommendation.objects.create(
                user=user,
                recommendation=recommendation,
                status='pending'
            )
            created_recommendations.append(user_recommendation)
        
        serializer = UserRecommendationSerializer(created_recommendations, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Обновляет статус рекомендации пользователя.
        """
        user_recommendation = self.get_object()
        serializer = UserRecommendationUpdateSerializer(
            user_recommendation, 
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(UserRecommendationSerializer(user_recommendation).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 