import os
from django.db import models
from django.conf import settings


def report_upload_path(instance, filename):
    # Generate a new file name: username_originalfilename
    username = instance.user.username
    base, ext = os.path.splitext(filename)
    return f"reports/{username}_{base}{ext}"


class MedicalReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    image = models.ImageField(upload_to='reports/')
    extracted_text = models.TextField(blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean_file_name(self):
        """Returns the file name without path or extension."""
        return os.path.splitext(os.path.basename(self.image.name))[0]

    def __str__(self):
        return self.clean_file_name()
