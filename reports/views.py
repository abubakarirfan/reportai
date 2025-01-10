from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import MedicalReportForm
from .models import MedicalReport
from django.contrib import messages
from .utils import extract_text_from_image, explain_medical_text
import os


@login_required
def upload_report(request):
    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the uploaded file
            uploaded_file = request.FILES.get('image')
            if uploaded_file:
                try:
                    # Save the file as a MedicalReport instance
                    report = MedicalReport(
                        user=request.user, image=uploaded_file)
                    report.save()

                    # Extract text from the uploaded image
                    extracted_text = extract_text_from_image(report.image.path)

                    # Check for medical keywords in the extracted text
                    medical_keywords = [
                        "diagnosis", "treatment", "prescription", "blood", "test", "pathology", "report"]
                    if not any(keyword in extracted_text.lower() for keyword in medical_keywords):
                        messages.error(
                            request, "The uploaded document does not appear to be a medical report.")
                        report.delete()  # Delete the invalid report
                        return redirect('upload_report')

                    # Generate explanation using Gemini API
                    explanation = explain_medical_text(extracted_text)

                    # Save extracted text and explanation
                    report.extracted_text = extracted_text
                    report.explanation = explanation
                    report.save()

                    messages.success(
                        request, "Report uploaded and processed successfully!")
                    return redirect('report_list')
                except Exception as e:
                    messages.error(request, f"Error processing the file: {e}")
            else:
                messages.error(request, "No file was uploaded.")
        else:
            messages.error(request, "Invalid form submission.")
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

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after signup
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def report_list(request):
    reports = MedicalReport.objects.filter(user=request.user)
    return render(request, 'reports/list.html', {'reports': reports})
