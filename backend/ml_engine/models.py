from django.db import models
from django.conf import settings


class SymptomAnalysis(models.Model):
    RISK_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='symptom_analyses')
    symptom_text = models.TextField()
    classification = models.CharField(max_length=200, blank=True)
    entities = models.JSONField(default=list)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='LOW')
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'symptom_analyses'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.classification} ({self.risk_level})'
