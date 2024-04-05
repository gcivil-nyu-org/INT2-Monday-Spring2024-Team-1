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


@login_required
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

        try:
            hospital_staff = HospitalStaff.objects.get(userID=current_user.id)
            userInfo["specialization"] = hospital_staff.specialization
        except HospitalStaff.DoesNotExist:
            userInfo["specialization"] = "None"

        return render(request, "user_profile.html", {"userInfo": userInfo})


@login_required
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


@login_required
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
        user_info = request.user
        story.append(Paragraph("Name: " + user_info.name, styles["Normal"]))
        story.append(Paragraph("DOB: " + user_info.dob, styles["Normal"]))
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


@login_required
def view_health_history_requests(request):
    zipped_details = get_health_history_details(request=request)
    return render(request, "view_requests.html", {"zipped_details": zipped_details})


@login_required
def record_sent_view(request):
    return render(request, "record_submit_complete.html")


def get_doctors(request, hos_id):
    doctorList = list(
        HospitalStaff.objects.filter(admin=False, hospitalID_id=hos_id).values()
    )
    return JsonResponse({"doctors": doctorList})


def get_record(request, rec_id):
    healthRecordList = list(HealthRecord.objects.filter(id=rec_id).values())

    return JsonResponse({"data": json.dumps(healthRecordList[0], default=str)})


def get_edit(request, rec_id):
    selected_record = list(HealthRecord.objects.filter(id=rec_id).values())
    app = list(
        Appointment.objects.filter(id=selected_record[0]["appointmentId_id"]).values()
    )

    hospitalList = list(Hospital.objects.all().values())
    unselectedHospitalList = []
    for hospital in hospitalList:
        if hospital["id"] == selected_record[0]["hospitalID"]:
            selected_record[0]["hospital_name"] = hospital["name"]
        else:
            unselectedHospitalList.append(hospital)

    doctorList = list(HospitalStaff.objects.filter(admin=False).values())

    unselectedDoctorList = []
    for docs in doctorList:
        if docs["id"] == selected_record[0]["doctorID"]:
            selected_record[0]["doctor_name"] = docs["name"]
        else:
            unselectedDoctorList.append(docs)

    data = {
        "appointment_props": app[0],
        "record": selected_record[0],
        "hospitals": unselectedHospitalList,
        "appointmentType": APPOINTMENT_TYPE,
        "appointmentProps": json.dumps(APPOINTMENT_PROPS),
        "doctors": unselectedDoctorList,
    }

    return render(request, "edit_health_record.html", {"data": data})


@login_required
def add_health_record_view(request):
    hospitalList = list(Hospital.objects.all().values())
    data = {
        "hospitals": hospitalList,
        "appointmentType": APPOINTMENT_TYPE,
        "appointmentProps": json.dumps(APPOINTMENT_PROPS),
    }

    # Add hospital id to data if user is an admin
    try:
        hospital_staff = HospitalStaff.objects.get(userID=request.user.id)
        hospitalID = hospital_staff.hospitalID
        data["hospitalID"] = hospitalID.id
    except HospitalStaff.DoesNotExist:
        pass

    if request.method == "POST":

        medicalDocUrl = file_upload(request, "medicalHistory")
        hospitalID = request.POST.get("hospitalID")
        doctorID = request.POST.get("doctorId")
        userEmail = request.POST.get("userEmail")
        # update userID to be either request.user or the userID of the email provided by the admin
        # if userEmail is populated then get the user id of that email else it'll be request.user
        if userEmail:
            try:
                userID = User.objects.get(email=userEmail)
            except User.DoesNotExist:
                context = {
                    "error_message": "No patient exists with this email address. Please try again."
                }
                return render(request, "record_submit.html", context)
        else:
            userID = request.user
        # create a new appointment
        appointmentType = APPOINTMENT_TYPE[request.POST.get("appointmentType")]
        appointmentProperties = dict()
        all_fields = request.POST

        medicalDocs = {request.POST.get("appointmentType"): medicalDocUrl}
        for key, value in all_fields.items():
            if (
                key != "csrfmiddlewaretoken"
                and key != "hospitalID"
                and key != "doctorId"
                and key != "appointmentType"
            ):
                appointmentProperties[key] = value
        appointmentProperties = json.dumps(appointmentProperties)
        new_appointment = Appointment.objects.create(
            name=appointmentType, properties=appointmentProperties
        )
        appointmentID = new_appointment

        HealthRecord.objects.create(
            doctorID=doctorID,
            userID=userID,
            hospitalID=hospitalID,
            appointmentId=appointmentID,
            healthDocuments=medicalDocs,
        )
        return redirect("new_health_record_sent")
    return render(request, "record_submit.html", {"data": data})


@login_required
def edit_health_record_view(request):
    if request.method == "POST":
        rec = json.loads(request.body)
        id = rec.get("recordId")
        record = get_object_or_404(HealthRecord, id=id)
        appID = rec.get("appointmentId")
        appointment = get_object_or_404(Appointment, id=appID)

        appointment.name = APPOINTMENT_TYPE[rec.get("appointmentType")]
        appointment.properties = json.dumps(rec.get("appointmentProperties"))
        appointment.save()

        record.doctorID = rec.get("doctorId")
        record.hospitalID = rec.get("hospitalID")
        record.status = "pending"
        record.appointmentId = appointment
        record.save()

        return JsonResponse({"message": "Updated succesfully"})


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
@csrf_exempt
def add_healthcare_staff(request):
    if request.user.is_authenticated and request.method == "POST":
        email = request.POST.get("email")
        fullname = request.POST.get("fullname")
        contactInfo = request.POST.get("contactInfo")
        is_admin = int(request.POST.get("is_admin"))
        specialization = request.POST.get("specialization")

        user_hospital_staff_entry = get_object_or_404(
            HospitalStaff, userID=request.user.id
        )
        hospital_id = user_hospital_staff_entry.hospitalID.id

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
@csrf_exempt
def deactivate_healthcare_staff(request):
    if request.user.is_authenticated and request.method == "PUT":
        updated_data = json.loads(request.body)
        user_ids = updated_data.get("user_ids", [])

        for user_id in user_ids:
            user = get_object_or_404(User, id=user_id)
            if not user.is_patient:
                user.is_active = False
                user.save()

        return JsonResponse(
            {"message": "Healthcare staff deactivated successfully"}, status=200
        )

    return JsonResponse({"error": "Unauthorized"}, status=401)


@login_required
@csrf_exempt
def activate_healthcare_staff(request):
    if request.user.is_authenticated and request.method == "PUT":
        updatedData = json.loads(request.body)
        user_id = updatedData.get("user_id")

        user = get_object_or_404(User, id=user_id)

        if user.is_patient:
            return JsonResponse(
                {"error": "Patient's account cannot be edited"}, status=400
            )

        user.is_active = True
        user.save()
        return JsonResponse(
            {"message": "Healthcare staff activated successfully"}, status=200
        )

    return JsonResponse({"error": "Unauthorized"}, status=401)


def community_home(request):
    return redirect("all_posts")


def view_all_posts(request):
    posts = Post.objects.all().order_by("-createdAt")
    return render(
        request, "community_home.html", {"posts": posts, "headerTitle": "All the posts"}
    )


def view_my_posts(request):
    posts = Post.objects.filter(user=request.user).order_by("-createdAt")
    return render(
        request, "community_home.html", {"posts": posts, "headerTitle": "My posts"}
    )


def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    return render(request, "post_details.html", {"post": post, "comments": comments})


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect("community")
    else:
        form = PostForm()
    return render(request, "post_create.html", {"form": form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("view_post", post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, "post_edit.html", {"form": form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "GET":
        post.delete()
        return redirect("community")
    return redirect("view_post", post_id=post_id)


@login_required
def create_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.commenter = request.user
            comment.save()

    return redirect("view_post", post_id=post.id)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == "GET":
        comment.delete()

    return redirect("view_post", post_id=comment.post.id)


@csrf_exempt
def request_health_history(request):
    if request.method == "POST":
        requestorName = request.POST.get("requestorName")
        requestorEmail = request.POST.get("requestorEmail")
        purpose = request.POST.get("purpose")
        userEmail = request.POST.get("userEmail")

        context = {"error_message:": ""}

        if not User.objects.filter(email=userEmail).exists():
            context["error_message"] = "No user account exists with this email"
            return render(request, "request_health_history.html", context)

        user = User.objects.get(email=userEmail)

        if not user.is_patient:
            context["error_message"] = "No user account exists with this email"
            return render(request, "request_health_history.html", context)

        HealthHistoryAccessRequest.objects.create(
            userID=user,
            requestorName=requestorName,
            requestorEmail=requestorEmail,
            purpose=purpose,
        )

        return redirect("homepage")

    return render(request, "request_health_history.html")


@login_required
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


@login_required
@csrf_exempt
def update_health_history_access_request_status(request):
    if request.user.is_authenticated and request.method == "PUT":
        updatedData = json.loads(request.body)
        request_id = updatedData.get("request_id")
        status = updatedData.get("status")

        request = get_object_or_404(HealthHistoryAccessRequest, id=request_id)

        request.status = status
        request.save()
        return JsonResponse(
            {"message": "Request status updated successfully"}, status=200
        )

    return JsonResponse({"error": "Unauthorized"}, status=401)

@login_required()
def update_request_status(request):
    if request.method == "POST":
        record_id = request.POST.get("record_id")
        decision = request.POST.get("decision")
        health_record = get_object_or_404(HealthRecord, id=record_id)
        if decision == "Approve":
            health_record.status = "approved"
        else:
            health_record.status = "rejected"
            health_record.rejectedReason = request.POST.get("reason")

        health_record.save()
        return JsonResponse(
            {"message": "Request status updated successfully"}, status=200
        )

    return redirect("manage_request")


