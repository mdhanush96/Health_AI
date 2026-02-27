from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            'id', 'file_name', 'report_type', 'extracted_text',
            'summary', 'status', 'uploaded_at', 'processed_at'
        ]
        read_only_fields = ['id', 'extracted_text', 'summary', 'status', 'uploaded_at', 'processed_at']


class ReportUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = Report
        fields = ['file']

    def validate_file(self, value):
        allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.csv']
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f'Unsupported file type. Allowed: {", ".join(allowed_extensions)}'
            )
        max_size = 20 * 1024 * 1024  # 20MB
        if value.size > max_size:
            raise serializers.ValidationError('File size must not exceed 20MB.')
        return value
