from django.db import models
from django.conf import settings


class EmergencyAlert(models.Model):
    SEVERITY_LEVELS = [
        ('LOW', 'Low - Monitor'),
        ('MEDIUM', 'Medium - See Doctor Soon'),
        ('HIGH', 'High - See Doctor Today'),
        ('CRITICAL', 'Critical - Call Emergency Services'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='emergency_alerts')
    symptom_text = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    triggered_keywords = models.JSONField(default=list)
    recommended_action = models.TextField()
    emergency_contact = models.CharField(max_length=50, default='911')
    is_acknowledged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'emergency_alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.severity} ({self.created_at.date()})'
