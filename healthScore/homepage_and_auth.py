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


def homepage(request):
    return render(request, "homepage.html")


@csrf_exempt
def registration(request):
    if request.method == "POST":
        role = request.POST.get("role")
        email = request.POST.get("email")
        password = request.POST.get("password")
        fullname = request.POST.get("fullname")
        phone_number = request.POST.get("contactInfo")
        context = {"error_message:": ""}

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.is_patient:
                context["error_message"] = (
                    "A patient account already exists with this email"
                )
            elif user.is_staff:
                context["error_message"] = (
                    "An admin account already exists with this email"
                )
            else:
                context["error_message"] = (
                    "A healthcare worker account already exists with this email"
                )

            return render(request, "registration.html", context)

        common_fields = {
            "email": email,
            "password": password,
            "name": fullname,
            "contactInfo": phone_number,
        }

        if role == "User":
            file_url = file_upload(request, "identityProof")
            user_specific_fields = {
                "dob": request.POST.get("dob"),
                "gender": request.POST.get("gender"),
                "address": f"{request.POST.get('street_address')}, {request.POST.get('city')}, {request.POST.get('state')}, {request.POST.get('zipcode')}",
                "proofOfIdentity": file_url,  # This needs handling for file upload
            }
            User.objects.create_patient(**common_fields, **user_specific_fields)

        elif role == "Healthcare Admin":
            hospital_name = request.POST.get("hospital_name")
            hospital_address = f"{request.POST.get('facility_street_address')}, {request.POST.get('facility_city')}, {request.POST.get('facility_state')}, {request.POST.get('facility_zipcode')}"

            user = User.objects.create_staff(**common_fields)

            hospital, created = Hospital.objects.get_or_create(
                name=hospital_name,
                defaults={"address": hospital_address, "contactInfo": phone_number},
            )

            HospitalStaff.objects.create(
                hospitalID=hospital,
                admin=True,
                name=fullname,
                contactInfo=phone_number,
                userID=user.id,
            )

        return redirect("homepage")

    return render(request, "registration.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password, is_active=True)

        if user is not None:
            login(request, user)
            return redirect("homepage")
        else:
            return render(
                request,
                "login.html",
                {"error_message": "Invalid email or password. Please try again."},
            )
    return render(request, "login.html")
