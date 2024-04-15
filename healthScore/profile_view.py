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


@login_required(login_url="/")
@csrf_exempt
def edit_user_info(request):
    if request.method == "POST":
        current_user = request.user

        new_email = request.POST.get("email")
        file_url = file_upload(request, "userProfile")
        if new_email and new_email != current_user.email:
            if (
                User.objects.exclude(id=current_user.id)
                .filter(email=new_email)
                .exists()
            ):
                return JsonResponse(
                    {
                        "error": "This email address is already being used by another account."
                    },
                    status=400,
                )

        data_updated = False

        for field in ["name", "email", "address", "contactInfo", "profilePic"]:
            new_value = request.POST.get(field)
            current_value = getattr(current_user, field)
            if new_value and new_value != current_value:
                if field == "profilePic":
                    setattr(current_user, field, file_url)
                setattr(current_user, field, new_value)
                data_updated = True

        new_specialization = request.POST.get("specialization")
        if new_specialization:
            try:
                hospital_staff = HospitalStaff.objects.get(userID=current_user.id)
                if hospital_staff.specialization != new_specialization:
                    hospital_staff.specialization = new_specialization
                    hospital_staff.save()
                    data_updated = True
            except HospitalStaff.DoesNotExist:
                pass

        if data_updated:
            current_user.save()
            return JsonResponse(
                {"message": "User information updated successfully"}, status=200
            )
        else:
            return JsonResponse({"message": "No data was changed."}, status=200)
    else:
        view_user_info(request)


@login_required(login_url="/")
def view_user_info(request):
    if request.method == "GET":
        current_user = request.user
        userInfo = {
            "email": current_user.email,
            "name": current_user.name,
            "dob": current_user.dob,
            "contactInfo": current_user.contactInfo,
            # dummy string for now. Needs to be replaced with the S3 string
            "proofOfIdentity": current_user.proofOfIdentity,
            "address": current_user.address,
            "gender": current_user.gender,
            "profilePic": current_user.profilePic,
            "bloodGroup": current_user.bloodGroup,
            "requests": json.dumps(current_user.requests),
        }

        try:
            hospital_staff = HospitalStaff.objects.get(userID=current_user.id)
            userInfo["specialization"] = hospital_staff.specialization
        except HospitalStaff.DoesNotExist:
            userInfo["specialization"] = "None"

        return render(request, "user_profile.html", {"userInfo": userInfo})

