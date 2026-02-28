import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from ml_engine.models import SymptomAnalysis
from .models import Recommendation
from .serializers import RecommendationSerializer
from .engine import get_recommendations

logger = logging.getLogger('health_ai')


class RecommendationView(APIView):
    """
    GET /api/recommend/?analysis_id=<id>
    Returns personalized health recommendations based on symptom analysis.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        analysis_id = request.query_params.get('analysis_id')

        if analysis_id:
            try:
                analysis = SymptomAnalysis.objects.get(id=analysis_id, user=request.user)
                category = analysis.classification
                risk_level = analysis.risk_level

                # Return cached recommendation if exists
                try:
                    rec = analysis.recommendation
                    return Response(RecommendationSerializer(rec).data)
                except Recommendation.DoesNotExist:
                    pass

                # Generate new recommendation
                recs = get_recommendations(category, risk_level)
                rec = Recommendation.objects.create(
                    user=request.user,
                    symptom_analysis=analysis,
                    **recs
                )
                return Response(RecommendationSerializer(rec).data)
            except SymptomAnalysis.DoesNotExist:
                return Response({'error': 'Analysis not found'}, status=status.HTTP_404_NOT_FOUND)

        # Return latest recommendation
        latest = Recommendation.objects.filter(user=request.user).first()
        if latest:
            return Response(RecommendationSerializer(latest).data)
        return Response({'detail': 'No recommendations available. Submit symptoms first.'}, status=status.HTTP_200_OK)


class RecommendationHistoryView(generics.ListAPIView):
    """List all recommendations for the authenticated user."""
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recommendation.objects.filter(user=self.request.user)
