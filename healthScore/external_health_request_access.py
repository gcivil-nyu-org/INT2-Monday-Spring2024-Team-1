from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
import json

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle

# To overcame issues with regards to permissions (POST calls will give CSRF errors if the below tag is not used)
from django.views.decorators.csrf import csrf_exempt

from healthConfig.settings import EMAIL_HOST_USER

from .models import (
    Appointment,
    HealthRecord,
    Hospital,
    User,
    HospitalStaff,
    Post,
    Comment,
    HealthHistoryAccessRequest,
)

from .user_utils import get_health_history_details
from .forms import PostForm, CommentForm
from .file_upload import file_upload
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail, EmailMessage
from .hospital_admin_utils import get_admin_health_history_details
from . import patient_view_records
from . import admin_view_user_healthrecords

DATE_FORMAT = "%Y-%m-%d"
APPOINTMENT_TYPE = {
    "blood_test": "Blood Test",
    "eye": "Eye Exams",
    "general": "General Physical",
    "dermatologist": "Dermatologist",
    "diabetes_screening": "Diabetes Screening",
    "dentist": "Dentist",
    "gynecologist": "Gynecologist",
    "vaccinations": "Vaccinations",
}

APPOINTMENT_PROPS = {
    "blood_test": {
        "blood_group": "Blood Group",
        "hemoglobin_count": "Hemoglobin Count",
        "date": "Date",
        "platelet_count": "Platelet Count",
    },
    "eye": {
        "cylindrical_power_right": "Cylindrical Power Right",
        "cylindrical_power_left": "Cylindrical Power Left",
        "spherical_power_left": "Spherical Power Left",
        "spherical_power_right": "Spherical Power Right",
        "date": "Date",
    },
    "general": {
        "blood_pressure": "Blood Pressure",
        "pulse_rate": "Pulse Rate",
        "date": "Date",
    },
    "dermatologist": {
        "care_received": "Care Received",
        "second_visit": "Second Visit Required",
        "date": "Date",
    },
    "diabetes_screening": {
        "fasting_sugar_level": "Fasting Sugar Level",
        "random_sugar_level": "Random Sugar Level",
        "second_visit": "Second Visit Required",
        "date": "Date",
    },
    "dentist": {
        "care_received": "Care Received",
        "second_visit": "Second Visit Required",
        "date": "Date",
    },
    "gynecologist": {
        "care_received": "Care Received",
        "second_visit": "Second Visit Required",
        "date": "Date",
    },
    "vaccinations": {
        "name": "Name",
        "type": "Vaccination Type",
        "dose_2": "Dose 2",
        "date": "Dose 2 Date",
    },
}



@csrf_exempt
def request_health_history(request):
    if request.method == "POST":
        requestorName = request.POST.get("requestorName")
        requestorEmail = request.POST.get("requestorEmail")
        purpose = request.POST.get("purpose")
        userEmail = request.POST.get("userEmail")
        userDob = request.POST.get("dob")

        context = {"error_message:": ""}

        if not User.objects.filter(email=userEmail, dob=userDob).exists():
            context["error_message"] = "No user account exists with these details"
            return render(request, "request_health_history.html", context)

        user = User.objects.get(email=userEmail, dob=userDob)

        if not user.is_patient:
            context["error_message"] = "No user account exists with these details"
            return render(request, "request_health_history.html", context)

        HealthHistoryAccessRequest.objects.create(
            userID=user,
            requestorName=requestorName,
            requestorEmail=requestorEmail,
            purpose=purpose,
        )

        return redirect("homepage")

    return render(request, "request_health_history.html")



@csrf_exempt
@require_http_methods(["POST"])
def send_approval_emails(request):
    data = json.loads(request.body)
    emails = data.get("emails", [])
    requestIds = data.get("requestIds", [])

    hr_ids = HealthRecord.objects.filter(
        userID=request.user, status="approved"
    ).values_list("id", flat=True)
    pdf = patient_view_records.view_report(request, hr_ids)

    for email in emails:
        email_msg = EmailMessage(
            f"Update on Health History Access of: {request.user.email}",
            f"Hi,\n\nYour request to access health history of {request.user.name} has been approved. Please find PDF report attached.\n\nRegards,\nHealth Score Team",
            EMAIL_HOST_USER,
            [email],
        )

        email_msg.attach(
            "Health_Records_" + request.user.email + ".pdf",
            pdf.getvalue(),
            "application/pdf",
        )

        email_msg.send()

    # set Approved status to selected request ids
    for id in requestIds:
        hhar = HealthHistoryAccessRequest.objects.get(id=id)
        hhar.status = "approved"
        hhar.save()

    return JsonResponse({"message": "Emails have been sent!"}, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def send_rejection_emails(request):
    data = json.loads(request.body)
    emails = data.get("emails", [])
    requestIds = data.get("requestIds", [])

    for email in emails:
        send_mail(
            f"Update on Health History Access of: {request.user.email}",
            f"Hi,\n\nYour request to access health history of {request.user.name} has been rejected.\n\nRegards,\nHealth Score Team",
            EMAIL_HOST_USER,
            [email],
        )

    # set Approved status to selected request ids
    for id in requestIds:
        hhar = HealthHistoryAccessRequest.objects.get(id=id)
        hhar.status = "rejected"
        hhar.save()

    return JsonResponse({"message": "Emails have been sent!"}, status=200)


@login_required(login_url="/")
def update_request_status(request):
    if request.method == "POST" and request.user.is_healthcare_worker:
        update = json.loads(request.body)
        record_id = update["recordID"]
        decision = update["status"]
        health_record = get_object_or_404(HealthRecord, id=record_id)
        if decision == "approved":
            health_record.status = "approved"
        else:
            health_record.status = "rejected"
            health_record.rejectedReason = update["reason"]

        health_record.save()
        return JsonResponse(
            {"message": "Request status updated successfully"}, status=200
        )

    return admin_view_user_healthrecords.view_healthworkers_user_record(request)

@login_required(login_url="/")
@csrf_exempt
def view_health_history_access_requests(request):
    if request.method == "GET":
        user = request.user
        access_requests = HealthHistoryAccessRequest.objects.filter(
            userID=user
        ).order_by("-createdAt")
        return render(
            request, "view_access_requests.html", {"access_requests": access_requests}
        )

    return JsonResponse({"error": "wrong access method"}, status=401)
