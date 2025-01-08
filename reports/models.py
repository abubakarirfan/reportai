# reports/models.py
from django.db import models
from django.contrib.auth.models import User


class MedicalReport(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='reports/')
    extracted_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.id} by {self.user}"
