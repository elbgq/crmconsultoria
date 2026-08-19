from django.apps import AppConfig

class OportunidadesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'oportunidades'

    def ready(self):
        from .models import Oportunidade, HistoricoEstagio  # ✅ import só aqui dentro
        # se for para registrar signals, é aqui que deve ficar