from rest_framework import serializers
from .models import SymptomAnalysis


class SymptomAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymptomAnalysis
        fields = [
            'id', 'symptom_text', 'classification', 'entities',
            'risk_level', 'confidence_score', 'created_at'
        ]
        read_only_fields = ['id', 'classification', 'entities', 'risk_level', 'confidence_score', 'created_at']


class SymptomQuerySerializer(serializers.Serializer):
    symptom_text = serializers.CharField(
        min_length=5,
        max_length=2000,
        help_text='Describe your symptoms in detail'
    )
