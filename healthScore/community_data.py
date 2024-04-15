from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
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

from healthConfig.settings import EMAIL_HOST_USER

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
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail, EmailMessage
from .hospital_admin_utils import get_admin_health_history_details

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
def community_home(request):
    return redirect("all_posts")


@login_required(login_url="/")
def view_all_posts(request):
    posts = Post.objects.all().order_by("-createdAt")
    posts_with_status_info = [
        {
            "id": post.id,
            "title": post.title,
            "description": post.description,
            "createdAt": post.createdAt,
            "is_healthcare_worker": post.user.is_healthcare_worker,
        }
        for post in posts
    ]
    return render(
        request,
        "community_home.html",
        {"posts": posts_with_status_info, "headerTitle": "All the posts"},
    )


@login_required(login_url="/")
def view_my_posts(request):
    posts = Post.objects.filter(user=request.user).order_by("-createdAt")
    return render(
        request, "community_home.html", {"posts": posts, "headerTitle": "My posts"}
    )


@login_required(login_url="/")
def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    return render(request, "post_details.html", {"post": post, "comments": comments})


@login_required(login_url="/")
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


@login_required(login_url="/")
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


@login_required(login_url="/")
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "GET":
        post.delete()
        return redirect("community")
    return redirect("view_post", post_id=post_id)


@login_required(login_url="/")
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


@login_required(login_url="/")
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == "GET":
        comment.delete()

    return redirect("view_post", post_id=comment.post.id)

