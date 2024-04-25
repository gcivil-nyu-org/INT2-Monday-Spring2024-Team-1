from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json

# To overcame issues with regards to permissions (POST calls will give CSRF errors if the below tag is not used)
from django.views.decorators.csrf import csrf_exempt

from .models import (
    User,
    HospitalStaff,
)

from .file_upload import file_upload


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

        if request.FILES.get("profile_picture"):
            setattr(current_user, "profilePic", file_url)
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
