from django.contrib.auth.models import User
import os
from django.db import models
from django.conf import settings


def report_upload_path(instance, filename):
    # Generate a new file name: username_originalfilename
    username = instance.user.username
    base, ext = os.path.splitext(filename)
    return f"reports/{username}_{base}{ext}"


class MedicalReport(models.Model):
    CATEGORY_CHOICES = [
        ('Blood Test', 'Blood Test'),
        ('X-Ray', 'X-Ray'),
        ('MRI Scan', 'MRI Scan'),
        ('Prescription', 'Prescription'),
        ('Pathology Report', 'Pathology Report'),
        ('Other', 'Other'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='reports/')
    created_at = models.DateTimeField(auto_now_add=True)
    extracted_text = models.TextField(blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    favorite = models.BooleanField(default=False)
    parent_report = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='versions'
    )  # Reference to the parent report
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default='Other')


    def clean_file_name(self):
        """Returns the file name without path or extension."""
        return os.path.splitext(os.path.basename(self.image.name))[0]

    def __str__(self):
        return f"{self.clean_file_name()} ({self.category})"

    @property
    def get_all_versions(self):
        """
        Retrieve all related versions of the report, excluding the current version.
        Includes:
        - The parent report if the current report is a child.
        - All child reports if the current report is a parent.
        """
        # Identify the root parent
        parent = self.parent_report if self.parent_report else self

        # Include the parent and all its child reports, excluding the current one
        return MedicalReport.objects.filter(
            models.Q(parent_report=parent) | models.Q(pk=parent.pk)
        ).exclude(pk=self.pk).order_by('created_at')
