# ghibgen/apps.py
from django.apps import AppConfig

class GhibgenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ghibgen"
    verbose_name = "Ghibli Image Generator"