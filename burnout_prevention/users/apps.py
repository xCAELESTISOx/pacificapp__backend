from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = 'burnout_prevention.users'
    verbose_name = _('Users')
    
    def ready(self):
        import burnout_prevention.users.signals 