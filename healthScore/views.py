from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
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

from .models import (
    # Appointment,
    HealthRecord,
    Hospital,
    User,
    HospitalStaff,
)

from .user_utils import get_health_history_details

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


def view_health_history(request):
    # Create a new QueryDict object with the desired parameters: fetch only approved records for health history page
    updated_params = request.GET.copy()
    updated_params["record_status"] = "approved"

    # Update request.GET with the modified QueryDict
    request.GET = updated_params

    zipped_details = get_health_history_details(request=request)
    return render(request, "view_history.html", {"zipped_details": zipped_details})


@login_required
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
        return render(request, "user_profile.html", {"userInfo": userInfo})


@login_required
@csrf_exempt
def edit_user_info(request):
    if request.method == "PUT":
        updatedData = json.loads(request.body)
        current_user = request.user

        new_email = updatedData.get("email")
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
            new_value = updatedData.get(field)
            current_value = getattr(current_user, field)
            if new_value and new_value != current_value:
                setattr(current_user, field, new_value)
                data_updated = True

        if data_updated:
            current_user.save()
            return JsonResponse(
                {"message": "User information updated successfully"}, status=200
            )
        else:
            return JsonResponse({"message": "No data was changed."}, status=200)


def view_report(request):
    if request.method == "POST":
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="Report.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        title_style = styles["Title"]
        title = "Health Records Report"
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 18))

        right_aligned_style = ParagraphStyle(
            "RightAligned", parent=styles["Normal"], alignment=TA_RIGHT
        )
        current_date = datetime.now().strftime(DATE_FORMAT)

        logo = "healthScore/static/HSlogo.jpg"
        logo_img = Image(logo, width=128, height=40)
        logo_and_date = [
            [logo_img, Paragraph("Date: " + current_date, right_aligned_style)]
        ]
        logo_and_date = Table(logo_and_date)
        logo_and_date.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )
        story.append(logo_and_date)
        user_id = 2
        user_info = User.objects.get(id=user_id)
        story.append(Paragraph("Name: " + user_info.name, styles["Normal"]))
        story.append(
            Paragraph("DOB: " + user_info.dob.strftime(DATE_FORMAT), styles["Normal"])
        )
        story.append(Paragraph("BloodGroup: " + user_info.bloodGroup, styles["Normal"]))
        story.append(Paragraph("Email: " + user_info.email, styles["Normal"]))
        story.append(Paragraph("Contact: " + user_info.contactInfo, styles["Normal"]))
        story.append(Paragraph("Address: " + user_info.address, styles["Normal"]))
        story.append(Spacer(1, 12))

        table_data = [
            [
                Paragraph("Reason for Visit"),
                Paragraph("Visit Details"),
                Paragraph("Healthcare Worker"),
                Paragraph("Healthcare Facility"),
                Paragraph("Address"),
                Paragraph("Date"),
                Paragraph("Properties"),
            ],
        ]

        selected_record_ids = request.POST.getlist("record_ids")
        for record_id in selected_record_ids:
            row = []
            record = HealthRecord.objects.get(id=record_id)
            appointment_pro = record.appointmentId.properties
            appointment_properties = json.loads(appointment_pro)
            appointment_name = record.appointmentId.name
            appointment_name_para = Paragraph(appointment_name)
            row.append(appointment_name_para)

            appointment_type = appointment_properties.get("type", "Unknown")
            appointment_type_para = Paragraph(appointment_type)
            row.append(appointment_type_para)

            doctor_name = HospitalStaff.objects.get(id=record.doctorID).name
            doctor_name_para = Paragraph(doctor_name)
            row.append(doctor_name_para)

            hospital_name = Hospital.objects.get(id=record.hospitalID).name
            hospital_name_para = Paragraph(hospital_name)
            row.append(hospital_name_para)

            hospital_addr = Hospital.objects.get(id=record.hospitalID).address
            hospital_addr_para = Paragraph(hospital_addr)
            row.append(hospital_addr_para)

            updated = record.updatedAt.strftime(DATE_FORMAT)
            updated_para = Paragraph(updated)
            row.append(updated_para)

            temp_row = []
            for rec, val in appointment_properties.items():
                if rec == "date":
                    val = datetime.strptime(val, "%Y-%m-%d %H:%M:%S.%f").strftime(
                        DATE_FORMAT
                    )

                temp_row.append(Paragraph(str(rec).capitalize() + " :   " + str(val)))
            row.append(temp_row)

            table_data.append(row)

        page_width, page_height = letter
        left_margin = right_margin = 50
        effective_page_width = page_width - (left_margin + right_margin)

        col_widths = [
            effective_page_width * 0.1,  # Reason for Visit
            effective_page_width * 0.15,  # Visit Details
            effective_page_width * 0.15,  # Healthcare Worker
            effective_page_width * 0.15,  # Healthcare Facility
            effective_page_width * 0.15,  # Address
            effective_page_width * 0.15,  # Date
            effective_page_width * 0.25,  # Properties
        ]
        table = Table(table_data, colWidths=col_widths)

        table_style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
            ]
        )

        table.setStyle(table_style)
        story.append(table)

        doc.build(story)
        return response


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
            user_specific_fields = {
                "dob": request.POST.get("dob"),
                "gender": request.POST.get("gender"),
                "address": f"{request.POST.get('street_address')}, {request.POST.get('city')}, {request.POST.get('state')}, {request.POST.get('zipcode')}",
                "proofOfIdentity": request.POST.get(
                    "identity_proof"
                ),  # This needs handling for file upload
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

        user = authenticate(request, email=email, password=password)

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


def view_health_history_requests(request):
    zipped_details = get_health_history_details(request=request)

    return render(request, "view_requests.html", {"zipped_details": zipped_details})


@login_required
@csrf_exempt
def get_hospitals(request):
    hospitalList = list(Hospital.objects.all().values())
    data = {
        "hospitals": hospitalList,
        "appointmentType": APPOINTMENT_TYPE,
        "appointmentProps": json.dumps(APPOINTMENT_PROPS),
    }
    return render(request, "submit_health_record.html", {"data": data})


@login_required
@csrf_exempt
def get_doctors(request, hos_id):
    doctorList = list(
        HospitalStaff.objects.filter(admin=False, hospitalID_id=hos_id).values()
    )
    return JsonResponse({"doctors": doctorList})


# def create_record(request):
#     print(request, "request")
#     updatedData = json.loads(request.body)
#     current_user = ""
#     current_user = request.user

#     current_user_id = current_user.id

#     new_record = Appointment.objects.create(
#         name=updatedData['appointmentType'],
#         properties=updatedData["appointmentProperties"]
#     )

#     HealthRecord.objects.create(
#         doctorID=updatedData['doctorId']
#         userID=current_user_id,
#         hospitalID=updatedData["hospitalID"],
#         appointmentId=new_record,
#         status="pending",
#     )


def get_facility_doctors(request):
    if request.user.is_authenticated:
        user_hospital_staff_entry = get_object_or_404(
            HospitalStaff, userID=request.user.id
        )
        hospital_id = user_hospital_staff_entry.hospitalID.id

        staff_members = HospitalStaff.objects.filter(
            hospitalID=hospital_id, admin=False
        )

        staff_data = []
        for staff in staff_members:
            try:
                user = User.objects.get(id=staff.userID)
                staff_data.append(
                    {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "contactInfo": staff.contactInfo,
                        "specialty": staff.specialization,
                        "is_active": user.is_active,
                    }
                )
            except User.DoesNotExist:
                continue

        return JsonResponse({"data": staff_data}, safe=False)

    return JsonResponse({"error": "Unauthorized"}, status=401)


def get_facility_admins(request):
    if request.user.is_authenticated:
        user_hospital_staff_entry = get_object_or_404(
            HospitalStaff, userID=request.user.id
        )
        hospital_id = user_hospital_staff_entry.hospitalID.id

        staff_members = HospitalStaff.objects.filter(hospitalID=hospital_id, admin=True)

        staff_data = []
        for staff in staff_members:
            try:
                user = User.objects.get(id=staff.userID)
                staff_data.append(
                    {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "contactInfo": staff.contactInfo,
                        "specialty": staff.specialization,
                        "is_active": user.is_active,
                    }
                )
            except User.DoesNotExist:

                continue

        return JsonResponse({"data": staff_data}, safe=False)

    return JsonResponse({"error": "Unauthorized"}, status=401)


def hospital_staff_directory(request):
    context = {
        "get_facility_doctors_url": "api/get-facility-doctors/",
        "get_facility_admins_url": "api/get-facility-admins/",
    }
    return render(request, "healthcare_facility.html", context)


@login_required
def add_healthcare_staff(request):
    if request.user.is_authenticated and request.method == "POST":
        email = request.POST.get("email")
        fullname = request.POST.get("fullname")
        contactInfo = request.POST.get("contactInfo")
        is_admin = int(request.POST.get("is_admin"))
        specialization = request.POST.get("specialization")
        hospital_id = request.POST.get("hospital_id")

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

            return render(request, "healthcare_facility.html", context)

        user_fields = {
            "email": email,
            "password": "dummy_password",  # healthcare worker will have to reset the password on first login
            "name": fullname,
            "contactInfo": contactInfo,
        }

        hospital = get_object_or_404(Hospital, id=hospital_id)

        user = None
        if is_admin:
            user = User.objects.create_staff(**user_fields)
        else:
            user = User.objects.create_healthcare_worker(**user_fields)

        HospitalStaff.objects.create(
            hospitalID=hospital,
            admin=is_admin,
            name=fullname,
            specialization=specialization,
            contactInfo=contactInfo,
            userID=user.id,
        )

        return redirect("hospital_staff_directory")

    return JsonResponse({"error": "Unauthorized"}, status=401)


@login_required
def deactivate_healthcare_staff(request):
    if request.user.is_authenticated and request.method == "PUT":
        updatedData = json.loads(request.body)
        user_id = updatedData.get("user_id")

        user = get_object_or_404(User, id=user_id)

        if user.is_patient:
            return JsonResponse(
                {"error": "Patient's account cannot be edited"}, status=400
            )

        user.is_active = 0
        user.save()
        return JsonResponse(
            {"message": "Healthcare staff deactivated successfully"}, status=200
        )

    return JsonResponse({"error": "Unauthorized"}, status=401)


@login_required
def activate_healthcare_staff(request):
    if request.user.is_authenticated and request.method == "PUT":
        updatedData = json.loads(request.body)
        user_id = updatedData.get("user_id")

        user = get_object_or_404(User, id=user_id)

        if user.is_patient:
            return JsonResponse(
                {"error": "Patient's account cannot be edited"}, status=400
            )

        user.is_active = 1
        user.save()
        return JsonResponse(
            {"message": "Healthcare staff activated successfully"}, status=200
        )

    return JsonResponse({"error": "Unauthorized"}, status=401)
