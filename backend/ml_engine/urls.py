from django.urls import path
from .views import SymptomAnalysisView

urlpatterns = [
    path('symptom/', SymptomAnalysisView.as_view(), name='symptom-analysis'),
]
