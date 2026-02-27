import logging
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Report
from .serializers import ReportSerializer, ReportUploadSerializer
from .ocr import extract_text_from_file, detect_report_type

logger = logging.getLogger('health_ai')


class ReportUploadView(generics.CreateAPIView):
    """Upload a medical report (PDF/Image/CSV). Text is extracted via OCR."""
    serializer_class = ReportUploadSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        report_type = detect_report_type(file.name)

        report = Report.objects.create(
            user=request.user,
            file=file,
            file_name=file.name,
            report_type=report_type,
            status='PROCESSING',
        )

        # Extract text immediately (async task would be better in production)
        try:
            extracted = extract_text_from_file(report.file.path, report_type)
            report.extracted_text = extracted
            report.status = 'COMPLETED'
            report.processed_at = timezone.now()
        except Exception as e:
            logger.error(f'Report processing failed: {e}')
            report.status = 'FAILED'
        report.save()

        return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)


class ReportAnalyzeView(generics.RetrieveAPIView):
    """Summarize an uploaded medical report using T5/BART."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        report_id = request.data.get('report_id')
        if not report_id:
            return Response({'error': 'report_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            report = Report.objects.get(id=report_id, user=request.user)
        except Report.DoesNotExist:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)

        if not report.extracted_text:
            return Response({'error': 'No text extracted from this report'}, status=status.HTTP_400_BAD_REQUEST)

        # Import summarizer lazily to avoid startup delay
        from ml_engine.summarizer import get_summarizer
        summarizer = get_summarizer()
        summary = summarizer.summarize(report.extracted_text)

        report.summary = summary
        report.save(update_fields=['summary'])

        return Response({
            'report_id': report.id,
            'summary': summary,
            'extracted_text': report.extracted_text[:500] + '...' if len(report.extracted_text) > 500 else report.extracted_text,
        })


class ReportListView(generics.ListAPIView):
    """List all reports for the authenticated user."""
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(user=self.request.user)
