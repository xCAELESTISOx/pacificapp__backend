from rest_framework import serializers
from burnout_prevention.recommendations.models import Recommendation, UserRecommendation


class RecommendationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рекомендаций.
    """
    class Meta:
        model = Recommendation
        fields = ['id', 'title', 'description', 'category', 'duration_minutes', 'is_quick', 'type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserRecommendationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рекомендаций пользователя.
    """
    recommendation = RecommendationSerializer(read_only=True)
    
    class Meta:
        model = UserRecommendation
        fields = ['id', 'user', 'recommendation', 'status', 'reason', 'user_feedback', 'user_rating', 'completed_at', 'created_at']
        read_only_fields = ['id', 'user', 'recommendation', 'created_at']


class UserRecommendationUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления статуса и обратной связи рекомендации пользователя.
    """
    class Meta:
        model = UserRecommendation
        fields = ['status', 'user_feedback', 'user_rating', 'completed_at']
        
    def validate_status(self, value):
        """
        Проверяет, что статус имеет допустимое значение.
        """
        valid_statuses = ['pending', 'accepted', 'completed', 'rejected']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value 