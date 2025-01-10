from django.db import models
from django.conf import settings


class MedicalReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    image = models.ImageField(upload_to='reports/')
    extracted_text = models.TextField(blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name
