from django import forms
from .models import MedicalReport


class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = ['image']
