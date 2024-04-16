from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json

# To overcame issues with regards to permissions (POST calls will give CSRF errors if the below tag is not used)
from django.views.decorators.csrf import csrf_exempt

from .models import (
    Hospital,
    User,
    HospitalStaff,
)


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


@login_required(login_url="/")
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


@login_required(login_url="/")
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


@login_required(login_url="/")
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
