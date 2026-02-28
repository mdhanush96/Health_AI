import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import SymptomAnalysis
from .serializers import SymptomQuerySerializer
from .classifier import get_classifier
from .clinical_decision_engine import get_clinical_decision_engine
from .constants import default_safe_response, safe_float, safe_string_list
from .rag_pipeline import get_rag_pipeline

logger = logging.getLogger('health_ai')


class SymptomAnalysisView(APIView):
    """
    POST /api/symptom/
    Hybrid clinical decision intelligence flow:
    1) ClinicalBERT classification
    2) Emergency rule check
    3) Structured recommendation + medication safety
    4) RAG educational explanation only
    """
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _build_safe_output(base_result: dict, condition: str, confidence: float, explanation: str) -> dict:
        fallback = default_safe_response(condition=condition, confidence=confidence)
        merged = {**fallback, **(base_result or {})}

        merged['condition'] = str(merged.get('condition') or fallback['condition'])
        merged['confidence'] = safe_float(merged.get('confidence', confidence), default=safe_float(confidence, 0.0))
        merged['diet'] = safe_string_list(merged.get('diet')) or fallback['diet']
        merged['exercise'] = safe_string_list(merged.get('exercise')) or fallback['exercise']
        merged['lifestyle'] = safe_string_list(merged.get('lifestyle')) or fallback['lifestyle']
        merged['safe_otc'] = safe_string_list(merged.get('safe_otc'))
        merged['specialist'] = str(merged.get('specialist') or fallback['specialist'])
        merged['emergency_flag'] = bool(merged.get('emergency_flag', merged.get('emergency', False)))
        merged['emergency'] = bool(merged.get('emergency', merged['emergency_flag']))
        merged['explanation'] = str(explanation or merged.get('explanation') or fallback['explanation'])
        merged['severity'] = str(merged.get('severity') or fallback['severity']).lower()

        if merged['emergency_flag']:
            merged['action'] = str(merged.get('action') or 'Immediate ER Visit')

        merged['educational_explanation'] = merged['explanation']
        return merged

    def post(self, request):
        symptom_text = ''
        condition = 'common_cold'
        confidence = 0.0
        risk_level = 'LOW'

        try:
            serializer = SymptomQuerySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            symptom_text = serializer.validated_data['symptom_text']

            classifier = get_classifier()
            condition, confidence, risk_level = classifier.classify(symptom_text)

            decision_engine = get_clinical_decision_engine()
            decision_result = decision_engine.generate_recommendation(
                symptom_text=symptom_text,
                condition=condition,
                severity=risk_level.lower(),
            )

            explanation = ''
            if not decision_result.get('emergency'):
                try:
                    rag_pipeline = get_rag_pipeline()
                    explanation = rag_pipeline.generate_educational_explanation(
                        query=symptom_text,
                        condition=decision_result.get('condition', condition),
                    )
                except Exception as rag_error:
                    logger.warning('RAG explanation failed, using template explanation: %s', rag_error)
                    explanation = (
                        'Educational explanation is temporarily unavailable. '
                        'Please follow structured recommendations and consult a qualified clinician if symptoms persist.'
                    )
            else:
                explanation = 'Emergency warning detected based on red-flag symptoms. Seek immediate medical care.'

            safe_payload = self._build_safe_output(decision_result, condition, confidence, explanation)

            SymptomAnalysis.objects.create(
                user=request.user,
                symptom_text=symptom_text,
                classification=safe_payload['condition'],
                risk_level=risk_level if str(risk_level).upper() in {'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'} else 'LOW',
                confidence_score=safe_payload['confidence'],
            )

            return Response(safe_payload, status=status.HTTP_200_OK)
        except Exception as pipeline_error:
            logger.exception('Symptom pipeline failed: %s', pipeline_error)
            fallback = self._build_safe_output(
                base_result=default_safe_response(condition=condition, confidence=confidence),
                condition=condition,
                confidence=confidence,
                explanation=(
                    'A processing issue occurred, so a safe fallback response is returned. '
                    'Please seek professional medical advice for ongoing symptoms.'
                ),
            )
            return Response(fallback, status=status.HTTP_200_OK)
