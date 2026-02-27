from django.db import models
from django.conf import settings


class Recommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    symptom_analysis = models.OneToOneField(
        'ml_engine.SymptomAnalysis',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='recommendation'
    )
    diet = models.JSONField(default=list)
    exercise = models.JSONField(default=list)
    lifestyle = models.JSONField(default=list)
    medicines = models.JSONField(default=list)
    specialist = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommendations'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.specialist} ({self.created_at.date()})'
