import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from .models import EmergencyAlert
from .serializers import EmergencyAlertSerializer, EmergencyCheckSerializer
from .detector import detect_emergency

logger = logging.getLogger('health_ai')


class EmergencyCheckView(APIView):
    """
    POST /api/emergency/
    Detects emergency severity from symptom text and logs the alert.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EmergencyCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        symptom_text = serializer.validated_data['symptom_text']

        result = detect_emergency(symptom_text)

        # Log all non-low severity alerts
        if result['severity'] != 'LOW':
            EmergencyAlert.objects.create(
                user=request.user,
                symptom_text=symptom_text,
                **result
            )

        return Response(result, status=status.HTTP_200_OK)


class EmergencyAlertsListView(generics.ListAPIView):
    """List all emergency alerts for the authenticated user."""
    serializer_class = EmergencyAlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EmergencyAlert.objects.filter(user=self.request.user)


class AcknowledgeAlertView(APIView):
    """Mark an emergency alert as acknowledged."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            alert = EmergencyAlert.objects.get(pk=pk, user=request.user)
            alert.is_acknowledged = True
            alert.save(update_fields=['is_acknowledged'])
            return Response(EmergencyAlertSerializer(alert).data)
        except EmergencyAlert.DoesNotExist:
            return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)
