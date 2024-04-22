from django.utils import timezone
from datetime import datetime, timedelta
from django.forms.models import model_to_dict
import json
from django.contrib.auth.decorators import login_required

from .models import (
    User,
    HealthRecord,
    Hospital,
    HospitalStaff,
    Appointment,
)


@login_required(login_url="/")
def get_health_history_details(request):
    if request.method == "GET":
        userID = request.user
        history_list = HealthRecord.objects.filter(userID=userID)

        appointment_name = request.GET.get("appointment_name")
        if appointment_name:
            history_list = history_list.filter(
                appointmentId__name__icontains=appointment_name
            )

        healthcare_worker = request.GET.get("healthcare_worker")
        if healthcare_worker:
            doctor_ids = HospitalStaff.objects.filter(
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
            hospital_ids = Hospital.objects.filter(
                name__icontains=healthcare_facility
            ).values_list("id", flat=True)
            history_list = history_list.filter(hospitalID__in=hospital_ids)

        # Filter records by status
        record_status = request.GET.get("record_status")
        if record_status:
            history_list = history_list.filter(status=record_status)

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

            # Append a dictionary for each record with all the details needed
            detailed_history_list.append(
                {
                    "record_id": h.id,
                    "doctor_name": doctor_name,
                    "hospital_name": hospital_name,
                    "hospital_address": hospital_address,
                    "createdAt": datetime.date(h.createdAt),
                    "updatedAt": datetime.date(h.updatedAt),
                    "appointment_name": appointment_name,
                    "appointment_type": appointment_type,
                    "rejectedReason": h.rejectedReason,
                    "record_status": h_details["status"],
                    "appointment_properties": json.dumps(appointment_properties),
                    "medicalFile": h.healthDocuments,
                }
            )

        zipped_details = zip(detailed_history_list, each_details)
        return zipped_details


def get_health_history_details_doctor(request):
    if request.method == "GET":
        userID = request.user
        history_list = HealthRecord.objects.filter(doctorID=userID.id)

        record_status = request.GET.get("record_status")
        if record_status:
            history_list = history_list.filter(status=record_status)

        appointment_name = request.GET.get("appointment_name")
        if appointment_name:
            history_list = history_list.filter(
                appointmentId__name__icontains=appointment_name
            )

        healthcare_worker = request.GET.get("healthcare_worker")
        if healthcare_worker:
            doctor_ids = HospitalStaff.objects.filter(
                name__icontains=healthcare_worker
            ).values_list("id", flat=True)
            history_list = history_list.filter(doctorID__in=doctor_ids)

        healthcare_facility = request.GET.get("healthcare_facility")
        if healthcare_facility:
            hospital_ids = Hospital.objects.filter(
                name__icontains=healthcare_facility
            ).values_list("id", flat=True)
            history_list = history_list.filter(hospitalID__in=hospital_ids)

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
                    "rejectedReason": h.rejectedReason,
                    "record_status": h_details["status"],
                    "appointment_properties": json.dumps(appointment_properties),
                    "medicalFile": h.healthDocuments,
                }
            )

        return detailed_history_list
