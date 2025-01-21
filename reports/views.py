from django.shortcuts import render, get_object_or_404
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import MedicalReportForm, RenameFileForm
from .models import MedicalReport
from django.contrib import messages
from .utils import extract_text_from_image, explain_medical_text
import os


@login_required
def upload_report(request):
    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES)
        if form.is_valid():
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
                            request,
                            f"The uploaded file '{uploaded_file.name}' does not appear to be a medical report. Please upload a valid medical document.", extra_tags='upload_page')
                        report.delete()  # Delete the invalid report
                        # Re-render with error
                        return render(request, 'reports/upload.html', {'form': form})

                    # Generate explanation using Gemini API
                    explanation = explain_medical_text(extracted_text)

                    # Save extracted text and explanation
                    report.extracted_text = extracted_text
                    report.explanation = explanation
                    report.save()

                    return redirect('report_detail', pk=report.pk)
                except Exception as e:
                    messages.error(
                        request, f"Error processing the file: {e}", extra_tags='upload_page')
            else:
                messages.error(request, "No file was uploaded.",
                               extra_tags='upload_page')
        else:
            messages.error(request, "Invalid form submission.",
                           extra_tags='upload_page')
    else:
        form = MedicalReportForm()
    return render(request, 'reports/upload.html', {'form': form})


@login_required
def report_detail(request, pk):
    # Retrieve the report for the logged-in user
    report = get_object_or_404(MedicalReport, pk=pk, user=request.user)

    # Explanation is already stored in the database, so no reprocessing is needed
    explanation = report.explanation

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
    paginator = Paginator(reports, 5)  # Show 10 reports per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'reports/list.html', {'page_obj': page_obj})


@login_required
def rename_report_file(request, pk):
    report = get_object_or_404(MedicalReport, pk=pk, user=request.user)

    if request.method == 'POST':
        form = RenameFileForm(request.POST)
        if form.is_valid():
            new_name = form.cleaned_data['new_name']
            old_file_path = report.image.path
            # Preserve original file extension
            file_extension = os.path.splitext(old_file_path)[1]
            new_file_path = os.path.join(
                os.path.dirname(old_file_path), f"{new_name}{file_extension}"
            )

            try:
                # Check if the new file name already exists
                if os.path.exists(new_file_path):
                    messages.error(
                        request, "A file with this name already exists. Please choose a different name.")
                else:
                    # Rename the physical file
                    os.rename(old_file_path, new_file_path)

                    # Update the database record
                    report.image.name = os.path.relpath(
                        new_file_path, settings.MEDIA_ROOT)
                    report.save()

                    messages.success(request, "File renamed successfully!")
                    return redirect('report_list')
            except Exception as e:
                messages.error(request, f"Error renaming file: {e}")
    else:
        form = RenameFileForm(initial={'new_name': os.path.splitext(
            report.image.name)[0]})  # Pre-fill with current name

    return render(request, 'reports/rename.html', {'form': form, 'report': report})


@login_required
def generate_pdf(request, pk):
    # Get the report for the logged-in user
    report = get_object_or_404(MedicalReport, pk=pk, user=request.user)

    # Render the HTML template for the PDF
    html = render_to_string('reports/pdf_template.html', {
        'report': report,
        'explanation': report.explanation  # Pass the explanation if available
    })

    # Create a response object to send the PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report.clean_file_name()}.pdf"'

    # Generate the PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    return response
