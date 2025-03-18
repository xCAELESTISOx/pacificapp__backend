from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from burnout_prevention.recommendations.models import Recommendation, UserRecommendation

User = get_user_model()

class Command(BaseCommand):
    help = 'Назначает рекомендации указанному пользователю'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email пользователя, которому назначаются рекомендации')

    def handle(self, *args, **options):
        email = options['email']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Пользователь с email {email} не найден!'))
            return
            
        # Получаем все рекомендации
        recommendations = Recommendation.objects.all()
        
        if not recommendations.exists():
            self.stdout.write(self.style.ERROR('В базе данных нет рекомендаций! Сначала создайте их с помощью команды create_test_data.'))
            return
            
        # Удаляем существующие рекомендации пользователя (опционально)
        UserRecommendation.objects.filter(user=user).delete()
        
        # Назначаем все рекомендации пользователю
        count = 0
        for recommendation in recommendations:
            UserRecommendation.objects.create(
                user=user,
                recommendation=recommendation,
                status='pending',
                reason='Автоматически назначено системой для тестирования'
            )
            count += 1
            
        self.stdout.write(self.style.SUCCESS(f'Успешно назначено {count} рекомендаций пользователю {user.email}!')) 