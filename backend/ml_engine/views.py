import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import SymptomAnalysis
from .serializers import SymptomQuerySerializer, SymptomAnalysisSerializer
from .classifier import get_classifier
from .rag import get_rag_system

logger = logging.getLogger('health_ai')


class SymptomAnalysisView(APIView):
    """
    POST /api/symptom/
    Analyzes symptom text using ClinicalBERT classification and RAG-based response generation.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SymptomQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        symptom_text = serializer.validated_data['symptom_text']

        # Classify symptoms
        classifier = get_classifier()
        category, confidence, risk_level = classifier.classify(symptom_text)

        # Generate grounded response via RAG
        rag = get_rag_system()
        rag_result = rag.generate_response(symptom_text, category)

        # Persist analysis
        analysis = SymptomAnalysis.objects.create(
            user=request.user,
            symptom_text=symptom_text,
            classification=category,
            risk_level=risk_level,
            confidence_score=confidence,
        )

        return Response({
            'analysis_id': analysis.id,
            'classification': category,
            'confidence_score': confidence,
            'risk_level': risk_level,
            'rag_response': rag_result['response'],
            'sources': rag_result['sources'],
            'retrieved_context': rag_result['retrieved_context'],
        }, status=status.HTTP_200_OK)
