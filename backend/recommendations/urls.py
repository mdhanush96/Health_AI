from django.urls import path
from .views import RecommendationView, RecommendationHistoryView

urlpatterns = [
    path('recommend/', RecommendationView.as_view(), name='recommendations'),
    path('recommend/history/', RecommendationHistoryView.as_view(), name='recommendation-history'),
]
