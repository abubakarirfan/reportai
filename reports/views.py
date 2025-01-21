from io import BytesIO
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
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


from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MedicalReport
from .forms import MedicalReportForm
from .utils import extract_text_from_image, explain_medical_text


@login_required
def upload_report(request, pk=None):
    """
    Handles uploading a new report or a new version of an existing report.

    If `pk` is provided, it assumes this is a new version of the report with ID `pk`.
    """
    parent_report = None

    # If pk is provided, get the parent report
    if pk:
        parent_report = get_object_or_404(
            MedicalReport, pk=pk, user=request.user)

    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES.get('image')
            if uploaded_file:
                try:
                    # Create a new MedicalReport instance
                    report = MedicalReport(
                        user=request.user,
                        image=uploaded_file,
                        parent_report=parent_report  # Set parent if this is a version
                    )
                    report.save()

                    # Extract text from the uploaded image
                    extracted_text = extract_text_from_image(report.image.path)

                    # Check for medical keywords in the extracted text
                    medical_keywords = [
                        "diagnosis", "treatment", "prescription", "blood", "test", "pathology", "report"]
                    if not any(keyword in extracted_text.lower() for keyword in medical_keywords):
                        messages.error(
                            request,
                            f"The uploaded file '{uploaded_file.name}' does not appear to be a medical report. Please upload a valid medical document.",
                            extra_tags='upload_page'
                        )
                        report.delete()  # Delete invalid report
                        return render(request, 'reports/upload.html', {'form': form})

                    # Generate explanation using Gemini API
                    explanation = explain_medical_text(extracted_text)

                    # Save extracted text and explanation
                    report.extracted_text = extracted_text
                    report.explanation = explanation
                    report.save()

                    messages.success(
                        request,
                        'Report uploaded successfully!' if not parent_report else 'New version uploaded successfully!'
                    )
                    return redirect('report_detail', pk=report.pk)
                except Exception as e:
                    messages.error(
                        request, f"Error processing the file: {e}", extra_tags='upload_page'
                    )
            else:
                messages.error(request, "No file was uploaded.",
                               extra_tags='upload_page')
        else:
            messages.error(request, "Invalid form submission.",
                           extra_tags='upload_page')
    else:
        form = MedicalReportForm()

    return render(request, 'reports/upload.html', {
        'form': form,
        'parent_report': parent_report
    })


@login_required
def toggle_favorite(request, pk):
    report = get_object_or_404(MedicalReport, pk=pk, user=request.user)
    report.favorite = not report.favorite
    report.save()
    return redirect('report_list')  # Redirect to the reports list page


@login_required
def report_detail(request, pk):
    report = get_object_or_404(MedicalReport, pk=pk, user=request.user)

    return render(request, 'reports/detail.html', {
        'report': report,
        'explanation': report.explanation,
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
    # Check if the user wants to view only favorites
    favorites_only = request.GET.get('favorites') == 'true'

    # Filter reports based on the user's request
    if favorites_only:
        reports = MedicalReport.objects.filter(
            user=request.user, favorite=True)
    else:
        reports = MedicalReport.objects.filter(user=request.user)

    # Paginate the results
    paginator = Paginator(reports, 5)  # Show 5 reports per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass additional context for filtering
    return render(request, 'reports/list.html', {
        'page_obj': page_obj,
        'favorites_only': favorites_only,  # Indicate if filtering by favorites
    })


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
    # Fetch the report and its version history
    report = get_object_or_404(MedicalReport, pk=pk, user=request.user)
    version_history = report.get_all_versions

    # Render the HTML content for the PDF
    html_content = render_to_string('reports/pdf_template.html', {
        'report': report,
        'version_history': version_history,
    })

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report.clean_file_name()}.pdf"'

    # Use BytesIO to hold the PDF in memory
    pdf_file = BytesIO()
    pisa_status = pisa.CreatePDF(
        BytesIO(html_content.encode('utf-8')), dest=pdf_file)

    # If PDF generation fails, return an error response
    if pisa_status.err:
        return HttpResponse('Error generating PDF.', status=500)

    # Write the generated PDF to the HTTP response
    pdf_file.seek(0)
    response.write(pdf_file.read())
    pdf_file.close()
    return response
