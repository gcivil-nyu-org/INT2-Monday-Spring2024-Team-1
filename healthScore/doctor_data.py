from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import (
    User,
    HospitalStaff,
)


@login_required(login_url="/")
def get_patients(request):
    patients = list(User.objects.filter(is_patient=True).values())
    return JsonResponse({"patients": patients})


@login_required(login_url="/")
def get_doctor_details(request, doctor_id):
    doctor = HospitalStaff.objects.filter(id=doctor_id).first()
    user_detail = list(User.objects.filter(id=doctor.userID).values())
    return JsonResponse({"user": user_detail})


@login_required(login_url="/")
def get_patient_details(request, patient_id):
    patient_detail = list(User.objects.filter(id=patient_id).values())
    return JsonResponse({"user": patient_detail})
