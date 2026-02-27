import logging
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import HealthHistory
from .serializers import HealthHistorySerializer

logger = logging.getLogger('health_ai')


class HealthHistoryListView(generics.ListAPIView):
    """
    GET /api/history/
    Returns paginated health history for the authenticated user.
    """
    serializer_class = HealthHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = HealthHistory.objects.filter(user=self.request.user)
        entry_type = self.request.query_params.get('type')
        if entry_type:
            queryset = queryset.filter(entry_type=entry_type.upper())
        return queryset
