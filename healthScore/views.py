from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
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
    HealthRecord,
    Hospital,
    User,
    HospitalStaff,
)

from .user_utils import get_health_history_details


def homepage(request):
    return render(request, "homepage.html")


def test_default_values(request):
    # To get all records from the  healthRecord table
    # healthRecordObjects = healthRecord.objects.all().values()
    # To create new records and save them
    # h = Hospital.objects.create(name="NYU", address="246", email="nyu@nyu.com", password="123435", contactInfo="123456781")

    return HttpResponse("<h1>Finally Workingggggggg. Welcome to HealthScore</h1>")


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
            "username": current_user.username,
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
        userID = int(updatedData.get("userId"))
        userData = ""
        try:
            userData = User.objects.filter(id=userID)
            if len(userData) == 0:
                raise Exception
        except Exception:
            return HttpResponse("User Invalid", status=500)

        userInformation = list(userData.values())[0]

        # print(userInformation['address'])
        userData.update(
            address=updatedData.get("address", userInformation["address"]),
            contactInfo=updatedData.get("contactInfo", userInformation["contactInfo"]),
            profilePic=updatedData.get("profilePic", userInformation["profilePic"]),
        )

        userData = User.objects.get(id=userID)
        return render(request, "user_profile.html", {"userUpdatedInfo": userData})


def view_report(request):
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
    current_date = datetime.now().strftime("%Y-%m-%d")

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

    user_id = 5
    user_info = User.objects.get(id=user_id)
    story.append(Paragraph("Name: " + user_info.name, styles["Normal"]))
    story.append(
        Paragraph("DOB: " + user_info.dob.strftime("%Y-%m-%d"), styles["Normal"])
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

        updated = record.updatedAt.strftime("%Y-%m-%d %H:%M")
        updated_para = Paragraph(updated)
        row.append(updated_para)
        table_data.append(row)

    page_width, page_height = letter
    left_margin = right_margin = 50
    effective_page_width = page_width - (left_margin + right_margin)

    col_widths = [
        effective_page_width * 0.1,  # Reason for Visit
        effective_page_width * 0.2,  # Visit Details
        effective_page_width * 0.15,  # Healthcare Worker
        effective_page_width * 0.15,  # Healthcare Facility
        effective_page_width * 0.15,  # Address
        effective_page_width * 0.15,  # Date
        effective_page_width * 0.2,  # Properties
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
    context = {
        "email": "",
        "username": "",
        "fullname": "",
        "dob": "",
        "gender": "",
        "street_address": "",
        "city": "",
        "state": "",
        "phone_number": "",
        "error_message": "",
    }

    if request.method == "POST":  # when the form is submitted
        context["email"] = email = request.POST.get("email")
        context["username"] = username = request.POST.get("username")
        context["fullname"] = fullname = request.POST.get("fullname")
        context["dob"] = dob = request.POST.get("dob")
        context["gender"] = gender = request.POST.get("gender")
        context["street_address"] = street_address = request.POST.get("street_address")
        context["city"] = city = request.POST.get("city")
        context["state"] = state = request.POST.get("state")
        context["phone_number"] = phone_number = request.POST.get("phone_number")
        # identity_proof = request.POST.get("identity_proof")

        if User.objects.filter(email=email).exists():
            context["error_message"] = (
                "An account already exists for this email address. Please log in."
            )
            return render(request, "registration.html", context)

        elif User.objects.filter(username=username).exists():
            context["error_message"] = (
                "Username already exists. Please choose a different one."
            )
            return render(request, "registration.html", context)

        else:
            hashed_password = make_password(request.POST.get("password"))

            User.objects.create(
                email=email,
                username=username,
                password=hashed_password,
                name=fullname,
                dob=dob,
                gender=gender,
                address=f"{street_address}, {city}, {state}",
                contactInfo=phone_number,
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


@csrf_exempt
def add_mock_data(request):
    if request.method == "POST":
        # Adding data to the Hospital table
        # hospital.objects.create(name="NYU Langone Health", address="424 E 34th St, New York, NY 10016", email="hospital_a@example.com", password="123456", contactInfo="123456781", status="approved")
        # hospital.objects.create(name="Mount Sinai Hospital", address="1468 Madison Ave, New York, NY 10029", email="hospital_b@example.com", password="123456", contactInfo="123456781", status="approved")
        # hospital.objects.create(name="CVS Pharmacy", address="305 East 86th St, New York, NY 10028", email="hospital_c@example.com", password="123456", contactInfo="123456781", status="approved")
        # hospital.objects.create(name="Duane Reade", address="1 Union Square South, New York, NY 10003", email="hospital_d@example.com", password="123456", contactInfo="123456781", status="approved")

        # Adding hospitalStaff data
        # hospitalStaff.objects.create(hospitalID=hospital.objects.get(id=5), admin=False, name="Dr. Steve Johnson", email="sj@langone.com", password="pass1234", specialization="Orthopedics", contactInfo="1234567890")
        # hospitalStaff.objects.create(hospitalID=hospital.objects.get(id=6), admin=False, name="Dr. Coco Gauff", email="cgauff@sinai.com", password="pass1234", specialization="Anesthesiology", contactInfo="1234567890")
        # hospitalStaff.objects.create(hospitalID=hospital.objects.get(id=7), admin=False, name="Carlos Alcaraz", email="ca@cvs.com", password="pass1234", specialization="", contactInfo="1234567890")
        # hospitalStaff.objects.create(hospitalID=hospital.objects.get(id=8), admin=False, name="Sofia Kenin", email="betty@duanereade.com", password="pass1234", specialization="", contactInfo="1234567890")
        # hospitalStaff.objects.create(hospitalID=hospital.objects.get(id=6), admin=False, name="Dr. Jannik Sinner", email="jsinner@sinai.com", password="pass1234", specialization="Psychiatry", contactInfo="1234567890")

        # Adding user data
        # user.objects.create(email="sgeier19@gmail.com", name="Sam Geier", password="userpass1", username="sgeier19", dob="1994-05-14", contactInfo="1234567890", proofOfIdentity="Proof1", address="70 Washington Square S, New York, NY 10012", securityQues="", securityAns="",bloodGroup="A+")

        # Adding appointment Data
        # appointment.objects.create(name="Vaccine", properties = json.dumps({"type":"Fluzone Sanofi", "dose_2": False, "date":datetime.datetime.now()}, default=str))
        # appointment.objects.create(name="Vaccine", properties = json.dumps({"type":"Comirnaty Pfizer", "dose_2": True, "date":datetime.datetime.now()}, default=str))
        # appointment.objects.create(name="Blood test", properties = json.dumps({"type":"Iron check", "dose_2": False, "date":datetime.datetime.now()}, default=str))
        # appointment.objects.create(name="MRI", properties = json.dumps({"type":"Bad back", "dose_2": False, "date":datetime.datetime.now()}, default=str))

        # healthRecord data
        # healthRecord.objects.create(doctorID=11, userID=user.objects.get(id=5), hospitalID=7, status="approved", createdAt=datetime.datetime.now(), updatedAt=datetime.datetime.now(), appointmentId=appointment.objects.get(id=5), healthDocuments="")
        # healthRecord.objects.create(doctorID=12, userID=user.objects.get(id=5), hospitalID=8, status="approved", createdAt=datetime.datetime.now(), updatedAt=datetime.datetime.now(), appointmentId=appointment.objects.get(id=6), healthDocuments="")
        # healthRecord.objects.create(doctorID=9, userID=user.objects.get(id=5), hospitalID=5, status="approved", createdAt=datetime.datetime.now(), updatedAt=datetime.datetime.now(), appointmentId=appointment.objects.get(id=7), healthDocuments="")
        # healthRecord.objects.create(doctorID=10, userID=user.objects.get(id=5), hospitalID=6, status="approved", createdAt=datetime.datetime.now(), updatedAt=datetime.datetime.now(), appointmentId=appointment.objects.get(id=8), healthDocuments="")
        return HttpResponse("Data Added to the database")
    else:
        return HttpResponse("Please change the request method to POST")


def view_health_history_requests(request):
    zipped_details = get_health_history_details(request=request)

    return render(request, "view_requests.html", {"zipped_details": zipped_details})
