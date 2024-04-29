from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .user_utils import get_health_history_details
from .models import (
    Post,
    HealthHistoryAccessRequest,
)


# To overcame issues with regards to permissions (POST calls will give CSRF errors if the below tag is not used)
from django.views.decorators.csrf import csrf_exempt

from .models import (
    Hospital,
    User,
    HospitalStaff,
)

from .file_upload import file_upload
from django.views.decorators.cache import never_cache


def homepage(request):
    return render(request, "homepage.html")


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
            "profilePic": "https://elasticbeanstalk-us-east-1-992382724291.s3.amazonaws.com/documents-health-score/userProfile/default/default-pic.png",
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


@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect("user_dashboard")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password, is_active=True)

        if user is not None:
            login(request, user)
            return redirect("user_dashboard")
        else:
            return render(
                request,
                "login.html",
                {"error_message": "Invalid email or password. Please try again."},
            )
    return render(request, "login.html")


@login_required(login_url="/")
def user_dashboard(request):
    if not request.user.is_patient:
        return redirect("homepage")

    posts = Post.objects.filter(user=request.user).order_by("-createdAt")[:5]

    updated_params = request.GET.copy()
    updated_params["record_status"] = "approved"

    request.GET = updated_params

    zipped_details = get_health_history_details(request=request)

    filtered_details = [
        details
        for details in zipped_details
        if details[0]["record_status"] == "approved"
    ]
    sorted_details = sorted(
        filtered_details, key=lambda x: x[0]["createdAt"], reverse=True
    )[:5]

    all_access_requests = HealthHistoryAccessRequest.objects.filter(
        userID=request.user
    ).order_by("-createdAt")

    total_requests = all_access_requests.count()

    recent_requests = all_access_requests[:5]

    context = {
        "posts": posts,
        "zipped_details": sorted_details,
        "access_requests": recent_requests,
        "total_requests": total_requests,
    }
    return render(request, "user_dashboard.html", context)
