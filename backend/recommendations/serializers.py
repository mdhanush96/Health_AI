from rest_framework import serializers
from .models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = [
            'id', 'diet', 'exercise', 'lifestyle', 'medicines',
            'specialist', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
