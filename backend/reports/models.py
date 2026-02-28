from django.db import models
from django.conf import settings


class Report(models.Model):
    REPORT_TYPES = [
        ('PDF', 'PDF Document'),
        ('IMAGE', 'Image'),
        ('CSV', 'CSV File'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    file = models.FileField(upload_to='reports/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    extracted_text = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'reports'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.user.email} - {self.file_name}'
