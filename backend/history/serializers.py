from rest_framework import serializers
from .models import HealthHistory


class HealthHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthHistory
        fields = ['id', 'entry_type', 'summary', 'metadata', 'created_at']
        read_only_fields = ['id', 'created_at']
