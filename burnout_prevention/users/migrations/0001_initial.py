# Generated by Django 4.2.10 on 2025-02-28 15:08

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('stress_level_base', models.IntegerField(default=50, help_text='Базовый уровень стресса от 0 до 100', verbose_name='базовый уровень стресса')),
                ('sleep_hours_avg', models.FloatField(blank=True, null=True, verbose_name='среднее время сна (часов)')),
                ('work_hours_daily', models.FloatField(blank=True, null=True, verbose_name='среднее рабочее время (часов в день)')),
                ('notifications_enabled', models.BooleanField(default=True)),
                ('notification_frequency', models.IntegerField(default=60, verbose_name='частота уведомлений (минуты)')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferred_relaxation_methods', models.JSONField(default=list, help_text='Список предпочитаемых методов релаксации', verbose_name='предпочитаемые методы релаксации')),
                ('work_start_time', models.TimeField(blank=True, null=True, verbose_name='время начала работы')),
                ('work_end_time', models.TimeField(blank=True, null=True, verbose_name='время окончания работы')),
                ('google_calendar_connected', models.BooleanField(default=False)),
                ('outlook_connected', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user profile',
                'verbose_name_plural': 'user profiles',
            },
        ),
        migrations.CreateModel(
            name='UserActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(choices=[('login', 'Вход в систему'), ('logout', 'Выход из системы'), ('profile_update', 'Обновление профиля'), ('recommendation_view', 'Просмотр рекомендации'), ('exercise_complete', 'Завершение упражнения'), ('survey_complete', 'Завершение опроса'), ('settings_change', 'Изменение настроек'), ('other', 'Другое')], max_length=50, verbose_name='тип активности')),
                ('description', models.TextField(blank=True, verbose_name='описание')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='время')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user activity',
                'verbose_name_plural': 'user activities',
                'ordering': ['-timestamp'],
            },
        ),
    ]
