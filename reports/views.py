from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from forms import MedicalReportForm
from models import MedicalReport
from utils import extract_text_from_image, explain_medical_text
import os


@login_required
def upload_report(request):
    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()

            # Run OCR and save the text
            image_path = report.image.path
            extracted_text = extract_text_from_image(image_path)
            report.extracted_text = extracted_text
            report.save()

            return redirect('report_detail', pk=report.pk)
    else:
        form = MedicalReportForm()
    return render(request, 'reports/upload.html', {'form': form})


@login_required
def report_detail(request, pk):
    report = MedicalReport.objects.get(pk=pk, user=request.user)

    explanation = None
    if report.extracted_text:
        explanation = explain_medical_text(report.extracted_text)

    return render(request, 'reports/detail.html', {
        'report': report,
        'explanation': explanation,
    })


