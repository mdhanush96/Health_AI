from django.urls import path
from .views import EmergencyCheckView, EmergencyAlertsListView, AcknowledgeAlertView

urlpatterns = [
    path('emergency/', EmergencyCheckView.as_view(), name='emergency-check'),
    path('emergency/alerts/', EmergencyAlertsListView.as_view(), name='emergency-alerts'),
    path('emergency/alerts/<int:pk>/acknowledge/', AcknowledgeAlertView.as_view(), name='acknowledge-alert'),
]
