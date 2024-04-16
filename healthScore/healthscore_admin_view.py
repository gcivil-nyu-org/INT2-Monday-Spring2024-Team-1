from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json

# To overcame issues with regards to permissions (POST calls will give CSRF errors if the below tag is not used)
from django.views.decorators.csrf import csrf_exempt

from .models import (
    Hospital,
)


@login_required(login_url="/")
def list_hospitals(request):
    if request.method == "GET":
        name_query = request.GET.get("name", "")
        status_query = request.GET.get("status", "")
        filters = {}
        if name_query:
            filters["name__icontains"] = name_query
        if status_query:
            filters["status"] = status_query

        hospitals = Hospital.objects.filter(**filters)
        return render(request, "hospital_list.html", {"hospitals": hospitals})


@login_required(login_url="/")
@csrf_exempt
def update_hospital_status(request, hospital_id):
    if request.method == "POST":
        hospital = get_object_or_404(Hospital, pk=hospital_id)
        bodyData = json.loads(request.body)
        new_status = bodyData.get("status")

        if new_status in ["active", "inactive", "pending"]:
            hospital.status = new_status
            hospital.save()
            return JsonResponse({"message": "Hospital status updated successfully."})
        else:
            return JsonResponse({"error": "Invalid status provided."}, status=400)
