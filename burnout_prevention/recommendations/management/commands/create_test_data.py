from django.core.management.base import BaseCommand
from burnout_prevention.recommendations.models import RecommendationType, Recommendation

class Command(BaseCommand):
    help = 'Создает тестовые данные для рекомендаций'

    def handle(self, *args, **options):
        # Создание типов рекомендаций
        self.stdout.write('Создание типов рекомендаций...')
        
        type_physical = RecommendationType.objects.create(
            name='Физические упражнения',
            description='Рекомендации по физической активности',
            icon='fitness_center'
        )
        
        type_mental = RecommendationType.objects.create(
            name='Ментальные практики',
            description='Рекомендации по медитации и ментальным практикам',
            icon='self_improvement'
        )
        
        type_social = RecommendationType.objects.create(
            name='Социальная активность',
            description='Рекомендации по социальному взаимодействию',
            icon='people'
        )
        
        type_work = RecommendationType.objects.create(
            name='Рабочие привычки',
            description='Рекомендации по организации рабочего времени',
            icon='work'
        )
        
        # Создание рекомендаций
        self.stdout.write('Создание рекомендаций...')
        
        # Физические упражнения
        Recommendation.objects.create(
            type=type_physical,
            title='Утренняя зарядка',
            description='Проведите 10 минут за утренней зарядкой для бодрости на весь день',
            duration_minutes=10,
            category='exercise',
            is_quick=True
        )
        
        Recommendation.objects.create(
            type=type_physical,
            title='Прогулка на свежем воздухе',
            description='Прогуляйтесь 30 минут на свежем воздухе для улучшения настроения и физического состояния',
            duration_minutes=30,
            category='exercise',
            is_quick=False
        )
        
        # Ментальные практики
        Recommendation.objects.create(
            type=type_mental,
            title='Медитация осознанности',
            description='5-минутная медитация для снятия стресса и повышения концентрации',
            duration_minutes=5,
            category='mindfulness',
            is_quick=True
        )
        
        Recommendation.objects.create(
            type=type_mental,
            title='Глубокое дыхание',
            description='Практика глубокого дыхания для снятия напряжения в течение рабочего дня',
            duration_minutes=3,
            category='mindfulness',
            is_quick=True
        )
        
        # Социальная активность
        Recommendation.objects.create(
            type=type_social,
            title='Кофе-брейк с коллегами',
            description='Проведите 15 минут за неформальным общением с коллегами',
            duration_minutes=15,
            category='social',
            is_quick=True
        )
        
        Recommendation.objects.create(
            type=type_social,
            title='Встреча с друзьями',
            description='Заранее запланируйте встречу с друзьями для отдыха и зарядки положительными эмоциями',
            duration_minutes=120,
            category='social',
            is_quick=False
        )
        
        # Рабочие привычки
        Recommendation.objects.create(
            type=type_work,
            title='Техника Помодоро',
            description='Работайте 25 минут, затем отдыхайте 5 минут. Повторите 4 раза, затем сделайте длинный перерыв',
            duration_minutes=25,
            category='work_balance',
            is_quick=True
        )
        
        Recommendation.objects.create(
            type=type_work,
            title='Планирование рабочего дня',
            description='Потратьте 15 минут на планирование задач на день для более эффективной работы',
            duration_minutes=15,
            category='work_balance',
            is_quick=True
        )
        
        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы!')) 