from django.urls import path
from .views import HealthHistoryListView

urlpatterns = [
    path('history/', HealthHistoryListView.as_view(), name='health-history'),
]
