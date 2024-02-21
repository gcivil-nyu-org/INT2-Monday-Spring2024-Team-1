from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
from .models import healthRecord, hospital, user


def test_default_values(request):
    # To get all records from the  healthRecord table
    healthRecordObjects = healthRecord.objects.all().values()      

    # To create new records and save them 
    # h = hospital.objects.create(name="NYU", address="246", email="nyu@nyu.com", password="123435", contactInfo="123456781")
    # h.save() 
    
    return HttpResponse(healthRecordObjects)
