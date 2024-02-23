from django.shortcuts import render
from django.http import HttpResponse
import datetime
import json

# To overcame issues with regards to permissions (POST calls will give CSRF errors if the below tag is not used)
from django.views.decorators.csrf import csrf_exempt

from .models import healthRecord, hospital, user, hospitalStaff, communityInteraction, appointment


def test_default_values(request):
    # To get all records from the  healthRecord table
    healthRecordObjects = healthRecord.objects.all().values()      
    # To create new records and save them 
    # h = hospital.objects.create(name="NYU", address="246", email="nyu@nyu.com", password="123435", contactInfo="123456781")
    return HttpResponse("<h1>Finaly Workingggggggg</h1>")


@csrf_exempt
def add_mock_data(request):
    if(request.method == "POST"):
        # Adding data to the Hospital table
        hospital.objects.create(name="Hospital A", address="Address A", email="hospital_a@example.com", password="123456", contactInfo="123456781", status="approved")
        hospital.objects.create(name="Hospital B", address="Address B", email="hospital_b@example.com", password="123456", contactInfo="123456781", status="pending")
        hospital.objects.create(name="Hospital C", address="Address C", email="hospital_c@example.com", password="123456", contactInfo="123456781", status="rejected")
        hospital.objects.create(name="Hospital D", address="Address D", email="hospital_d@example.com", password="123456", contactInfo="123456781", status="pending")

        # Adding hospitalStaff data
        # hospitalStaff.objects.create(hospitalID=hospital.objects.get(id=1), admin=True, name="Admin A", email="admin_a@hospitala.com", password="pass1234", specialization="", contactInfo="1234567890")
        # hospitalStaff.objects.create(hospitalID=hospital.objects.get(id=1), admin=False, name="Doctor A", email="doctor_a@hospitala.com", password="pass1234", specialization="Anesthesiology", contactInfo="1234567890")
        # hospitalStaff.objects.create(hospitalID=hospital.objects.get(id=2), admin=True, name="Admin B", email="admin_b@hospitalb.com", password="pass1234", specialization="", contactInfo="1234567890")
        # hospitalStaff.objects.create(hospitalID=hospital.objects.get(id=2), admin=False, name="Doctor B", email="doctor_b@hospitalb.com", password="pass1234", specialization="Cardiology", contactInfo="1234567890")
        # hospitalStaff.objects.create(hospitalID=hospital.objects.get(id=3), admin=True, name="Admin C", email="admin_c@hospitalc.com", password="pass1234", specialization="", contactInfo="1234567890")
        # hospitalStaff.objects.create(hospitalID=hospital.objects.get(id=3), admin=False, name="Doctor C", email="doctor_c@hospitalc.com", password="pass1234", specialization="Dermatology", contactInfo="1234567890")
        # hospitalStaff.objects.create(hospitalID=hospital.objects.get(id=4), admin=True, name="Admin D", email="admin_d@hospitald.com", password="pass1234", specialization="", contactInfo="1234567890")
        # hospitalStaff.objects.create(hospitalID=hospital.objects.get(id=4), admin=False, name="Doctor D", email="doctor_d@hospitald.com", password="pass1234", specialization="Forensic Pathology", contactInfo="1234567890")

        # Adding user data
        # user.objects.create(email="user1@example.com", name="User1", password="userpass1", userName="user1", dob="1990-01-01", contactInfo="1234567890", proofOfIdentity="Proof1", address="Address1", securityQues="", securityAns="",bloodGroup="A+")
        # user.objects.create(email="user2@example.com", name="User2", password="userpass2", userName="user2", dob="1990-01-01", contactInfo="1234567890", proofOfIdentity="Proof2", address="Address2", securityQues="", securityAns="",bloodGroup="B+")
        # user.objects.create(email="user3@example.com", name="User3", password="userpass3", userName="user3", dob="1990-01-01", contactInfo="1234567890", proofOfIdentity="Proof3", address="Address3", securityQues="", securityAns="",bloodGroup="O+")
        # user.objects.create(email="user4@example.com", name="User4", password="userpass4", userName="user4", dob="1990-01-01", contactInfo="1234567890", proofOfIdentity="Proof4", address="Address4", securityQues="", securityAns="",bloodGroup="AB+")

        # Adding appointment Data
        # appointment.objects.create(name="Vaccine", properties = json.dumps({"type":"vaccine A", "dose_2": False, "date":datetime.datetime.now()}, default=str))
        # appointment.objects.create(name="Vaccine", properties = json.dumps({"type":"vaccine A", "dose_2": True, "date":datetime.datetime.now()}, default=str))
        # appointment.objects.create(name="Blood test", properties = json.dumps({"type":"Iron check", "dose_2": False, "date":datetime.datetime.now()}, default=str))
        # appointment.objects.create(name="MRI", properties = json.dumps({"type":"N/A", "dose_2": False, "date":datetime.datetime.now()}, default=str))

        # healthRecord data 
        # healthRecord.objects.create(doctorID=1, userID=user.objects.get(id=1), hospitalID=1, status="approved", createdAt=datetime.datetime.now(), updatedAt=datetime.datetime.now(), appointmentId=appointment.objects.get(id=1), healthDocuments="")
        # healthRecord.objects.create(doctorID=2, userID=user.objects.get(id=2), hospitalID=2, status="rejected", createdAt=datetime.datetime.now(), updatedAt=datetime.datetime.now(), appointmentId=appointment.objects.get(id=2), healthDocuments="")
        # healthRecord.objects.create(doctorID=3, userID=user.objects.get(id=3), hospitalID=3, status="approved", createdAt=datetime.datetime.now(), updatedAt=datetime.datetime.now(), appointmentId=appointment.objects.get(id=3), healthDocuments="")
        # healthRecord.objects.create(doctorID=4, userID=user.objects.get(id=4), hospitalID=4, status="pending", createdAt=datetime.datetime.now(), updatedAt=datetime.datetime.now(), appointmentId=appointment.objects.get(id=4), healthDocuments="")
        return HttpResponse("Data Added to the database")
    else:
        return HttpResponse("Please change the request method to POST")
