# my_app/apps.py

from django.apps import AppConfig


class MyAppConfig(AppConfig): 
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my_app' 
    verbose_name = "Zarządzanie Wydatkami"

    def ready(self):
        
        pass 