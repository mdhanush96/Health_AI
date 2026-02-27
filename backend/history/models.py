from django.db import models
from django.conf import settings


class HealthHistory(models.Model):
    """Longitudinal health history tracking for a user."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='health_history')
    symptom_analysis = models.ForeignKey(
        'ml_engine.SymptomAnalysis',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='history_entries'
    )
    report = models.ForeignKey(
        'reports.Report',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='history_entries'
    )
    entry_type = models.CharField(
        max_length=20,
        choices=[
            ('SYMPTOM', 'Symptom Analysis'),
            ('REPORT', 'Medical Report'),
            ('RECOMMENDATION', 'Recommendation'),
            ('EMERGENCY', 'Emergency Alert'),
        ]
    )
    summary = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'health_history'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.entry_type} ({self.created_at.date()})'
