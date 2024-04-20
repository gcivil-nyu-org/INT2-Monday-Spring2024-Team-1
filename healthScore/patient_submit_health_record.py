from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json

from .models import (
    Appointment,
    HealthRecord,
    Hospital,
    User,
    HospitalStaff,
)

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


def get_doctors(request, hos_id):
    doctorList = list(
        HospitalStaff.objects.filter(admin=False, hospitalID_id=hos_id).values()
    )
    return JsonResponse({"doctors": doctorList})


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


@login_required(login_url="/")
def edit_health_record_view(request):
    if request.method == "POST":
        id = request.POST.get("recordId")
        record = get_object_or_404(HealthRecord, id=id)
        appID = request.POST.get("appointmentId")
        appointment = get_object_or_404(Appointment, id=appID)

        appointment.name = APPOINTMENT_TYPE[request.POST.get("appointmentType")]
        props = dict()
        for key in request.POST:
            if key not in [
                "hospitalID",
                "doctorId",
                "appointmentType",
                "recordId",
                "appointmentId",
                "csrfmiddlewaretoken",
            ]:
                props[key] = request.POST.get(key)

        appointment.properties = json.dumps(props)
        appointment.save()

        file_url = file_upload(request, "medicalHistory")
        record.doctorID = request.POST.get("doctorId")
        record.hospitalID = request.POST.get("hospitalID")
        record.status = "pending"
        record.appointmentId = appointment
        record.healthDocuments = file_url

        record.save()

        if request.user.is_staff:
            return redirect("admin_view_records")

        return redirect("view_requests")


@login_required(login_url="/")
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

        medicalDocs = medicalDocUrl
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


@login_required(login_url="/")
def record_sent_view(request):
    return render(request, "record_submit_complete.html")
