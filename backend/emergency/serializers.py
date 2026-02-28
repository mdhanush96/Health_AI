from rest_framework import serializers
from .models import EmergencyAlert


class EmergencyAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyAlert
        fields = [
            'id', 'symptom_text', 'severity', 'triggered_keywords',
            'recommended_action', 'emergency_contact', 'is_acknowledged', 'created_at'
        ]
        read_only_fields = ['id', 'severity', 'triggered_keywords', 'recommended_action', 'emergency_contact', 'created_at']


class EmergencyCheckSerializer(serializers.Serializer):
    symptom_text = serializers.CharField(min_length=5, max_length=2000)
