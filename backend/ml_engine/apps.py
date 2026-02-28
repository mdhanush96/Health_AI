from django.apps import AppConfig


class MlEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ml_engine'

    def ready(self):
        try:
            from .clinical_data_store import warmup_clinical_data_store
            warmup_clinical_data_store()
        except Exception:
            pass
