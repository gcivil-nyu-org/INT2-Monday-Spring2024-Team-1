from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
import json


from .models import (
    Appointment,
    HealthRecord,
    Hospital,
    User,
    HospitalStaff,
)

from .hospital_admin_utils import get_admin_health_history_details

from . import homepage_and_auth


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
def view_healthworkers_user_record(request):
    if request.method == "GET" and request.user.is_healthcare_worker:
        current_user = request.user
        doc_id = HospitalStaff.objects.get(userID=current_user.id).id
        history_list = HealthRecord.objects.filter(doctorID=doc_id)

        appointment_name = request.GET.get("appointment_name")
        if appointment_name:
            history_list = history_list.filter(
                appointmentId__name__icontains=appointment_name
            )

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

        history_list = history_list.filter(status="pending")

        detailed_history_list = []
        each_details = []
        for h in history_list:
            h_details = model_to_dict(h)
            each_details.append(h_details)
            # Fetch related appointment details
            appointment_details = Appointment.objects.get(id=h.appointmentId_id)
            appointment_name = appointment_details.name
            appointment_properties = json.loads(h.appointmentId.properties)
            appointment_type = (
                appointment_details.name
                if appointment_details.name is not None
                else "Unknown"
            )

            # Fetch healthcare worker details by Dr. ID
            doctor_details = HospitalStaff.objects.get(id=h.doctorID)
            doctor_name = doctor_details.name

            # Fetch hospital details by hospitalID
            hospital_details = Hospital.objects.get(id=h.hospitalID)
            hospital_name = hospital_details.name
            hospital_address = hospital_details.address

            user_email = User.objects.get(id=h.userID_id).email
            # Append a dictionary for each record with all the details needed
            detailed_history_list.append(
                {
                    "record_id": h.id,
                    "user_id": user_email,
                    "doctor_name": doctor_name,
                    "hospital_name": hospital_name,
                    "hospital_address": hospital_address,
                    "createdAt": datetime.date(h.createdAt),
                    "updatedAt": datetime.date(h.updatedAt),
                    "appointment_name": appointment_name,
                    "appointment_type": appointment_type,
                    "record_status": h_details["status"],
                    "appointment_properties": json.dumps(appointment_properties),
                }
            )

        zipped_details = detailed_history_list
        # return zipped_details
        return render(
            request, "view_records_doctors.html", {"docs_records": zipped_details}
        )

    return homepage_and_auth.homepage(request)


@login_required(login_url="/")
def admin_view_health_history_requests(request):
    zipped_details = get_admin_health_history_details(request=request)
    return render(
        request, "admin_view_records.html", {"zipped_details": zipped_details}
    )


@login_required(login_url="/")
def get_admin_edit(request, rec_id):
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

    record_email = User.objects.get(id=selected_record[0]["userID_id"]).email

    data = {
        "email": record_email,
        "appointment_props": app[0],
        "record": selected_record[0],
        "hospitals": unselectedHospitalList,
        "appointmentType": APPOINTMENT_TYPE,
        "appointmentProps": json.dumps(APPOINTMENT_PROPS),
        "doctors": unselectedDoctorList,
    }

    return render(request, "admin_edit_health_record.html", {"data": data})
