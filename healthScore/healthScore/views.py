from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json

# To overcame issues with regards to permissions (POST calls will give CSRF errors if the below tag is not used)
from django.views.decorators.csrf import csrf_exempt

from .models import (
    healthRecord,
    hospital,
    user,
    hospitalStaff,
    # communityInteraction,
    appointment,
)


def test_default_values(request):
    # To get all records from the  healthRecord table
    # healthRecordObjects = healthRecord.objects.all().values()
    # To create new records and save them
    # h = hospital.objects.create(name="NYU", address="246", email="nyu@nyu.com", password="123435", contactInfo="123456781")

    return HttpResponse("<h1>Finally Workingggggggg. Welcome to HealthScore</h1>")


def view_health_history(request):
    if request.method == "GET":
        # Filtering to just userID=5 to simulate it being a users view.
        history_list = healthRecord.objects.filter(userID=5)

        appointment_name = request.GET.get("appointment_name")
        if appointment_name:
            history_list = history_list.filter(
                appointmentId__name__icontains=appointment_name
            )

        healthcare_worker = request.GET.get("healthcare_worker")
        if healthcare_worker:
            doctor_ids = hospitalStaff.objects.filter(
                name__icontains=healthcare_worker
            ).values_list("id", flat=True)
            history_list = history_list.filter(doctorID__in=doctor_ids)

        filter_date = request.GET.get("date")
        if filter_date:
            filter_date = datetime.strptime(filter_date, "%Y-%m-%d").date()
            current_tz = timezone.get_current_timezone()
            start_of_day = timezone.make_aware(
                datetime.combine(filter_date, datetime.min.time()), current_tz
            )
            end_of_day = start_of_day + timedelta(days=1)
            history_list = history_list.filter(
                createdAt__range=(start_of_day, end_of_day)
            )

        healthcare_facility = request.GET.get("healthcare_facility")
        if healthcare_facility:
            hospital_ids = hospital.objects.filter(
                name__icontains=healthcare_facility
            ).values_list("id", flat=True)
            history_list = history_list.filter(hospitalID__in=hospital_ids)

        detailed_history_list = []

        for h in history_list:
            # Fetch related appointment details
            appointment_details = appointment.objects.get(id=h.appointmentId_id)
            appointment_name = appointment_details.name
            appointment_properties = json.loads(h.appointmentId.properties)
            appointment_type = appointment_properties.get("type", "Unknown")

            # Fetch healthcare worker details by Dr. ID
            doctor_details = hospitalStaff.objects.get(id=h.doctorID)
            doctor_name = doctor_details.name

            # Fetch hospital details by hospitalID
            hospital_details = hospital.objects.get(id=h.hospitalID)
            hospital_name = hospital_details.name
            hospital_address = hospital_details.address

            # Append a dictionary for each record with all the details needed
            detailed_history_list.append(
                {
                    "doctor_name": doctor_name,
                    "hospital_name": hospital_name,
                    "hospital_address": hospital_address,
                    "createdAt": datetime.date(h.createdAt),
                    "updatedAt": datetime.date(h.updatedAt),
                    "appointment_name": appointment_name,
                    "appointment_type": appointment_type,
                }
            )

    return render(request, "view_history.html", {"history_list": detailed_history_list})


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
        # user.objects.create(email="sgeier19@gmail.com", name="Sam Geier", password="userpass1", userName="sgeier19", dob="1994-05-14", contactInfo="1234567890", proofOfIdentity="Proof1", address="70 Washington Square S, New York, NY 10012", securityQues="", securityAns="",bloodGroup="A+")

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


@csrf_exempt
def register(request):
    if request.method == "POST":  # when the form is submitted
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        fullname = request.POST.get("fullname")
        dob = request.POST.get("dob")
        gender = request.POST.get("gender")
        street_address = request.POST.get("street_address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        phone_number = request.POST.get("phone_number")
        # identity_proof = request.POST.get("identity_proof")

        if not user.objects.filter(email=email).exists():
            user.objects.create(
                email=email,
                userName=username,
                password=password,
                name=fullname,
                dob=dob,
                gender=gender,
                address=street_address + ", " + city + ", " + state,
                contactInfo=phone_number,
            )
            # when successfully created an account
            return redirect("index")
        else:
            # when an email has registered already
            pass
    return render(request, "registration.html")
