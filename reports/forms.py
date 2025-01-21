from django import forms
from .models import MedicalReport


class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = ['image']


class RenameFileForm(forms.Form):
    new_name = forms.CharField(
        max_length=255,
        label="New File Name",
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter new file name'}),
    )
