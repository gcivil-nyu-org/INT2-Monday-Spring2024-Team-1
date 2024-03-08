from django.test import TestCase, RequestFactory
from django.urls import reverse

from datetime import datetime
import json

from healthScore.models import (
    healthRecord,
    hospital,
    user,
    hospitalStaff,
    appointment,
)
from healthScore.views import view_health_history, view_health_history_requests


class viewHealthHistoryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Adding data to the Hospital table
        h1 = hospital.objects.create(
            name="Hospital A",
            address="Address A",
            email="hospital_a@example.com",
            password="123456",
            contactInfo="123456781",
            status="approved",
        )
        h2 = hospital.objects.create(
            name="Hospital B",
            address="Address B",
            email="hospital_b@example.com",
            password="123456",
            contactInfo="123456781",
            status="pending",
        )
        h3 = hospital.objects.create(
            name="Hospital C",
            address="Address C",
            email="hospital_c@example.com",
            password="123456",
            contactInfo="123456781",
            status="rejected",
        )
        h4 = hospital.objects.create(
            name="Hospital D",
            address="Address D",
            email="hospital_d@example.com",
            password="123456",
            contactInfo="123456781",
            status="pending",
        )

        # Adding hospitalStaff data
        hospitalStaff.objects.create(
            hospitalID=h1,
            admin=True,
            name="Admin A",
            email="admin_a@hospitala.com",
            password="pass1234",
            specialization="",
            contactInfo="1234567890",
        )
        hospitalStaff.objects.create(
            hospitalID=h1,
            admin=False,
            name="Doctor A",
            email="doctor_a@hospitala.com",
            password="pass1234",
            specialization="Anesthesiology",
            contactInfo="1234567890",
        )
        hospitalStaff.objects.create(
            hospitalID=h2,
            admin=True,
            name="Admin B",
            email="admin_b@hospitalb.com",
            password="pass1234",
            specialization="",
            contactInfo="1234567890",
        )
        hospitalStaff.objects.create(
            hospitalID=h2,
            admin=False,
            name="Doctor B",
            email="doctor_b@hospitalb.com",
            password="pass1234",
            specialization="Cardiology",
            contactInfo="1234567890",
        )
        hospitalStaff.objects.create(
            hospitalID=h3,
            admin=True,
            name="Admin C",
            email="admin_c@hospitalc.com",
            password="pass1234",
            specialization="",
            contactInfo="1234567890",
        )
        hospitalStaff.objects.create(
            hospitalID=h3,
            admin=False,
            name="Doctor C",
            email="doctor_c@hospitalc.com",
            password="pass1234",
            specialization="Dermatology",
            contactInfo="1234567890",
        )
        hospitalStaff.objects.create(
            hospitalID=h4,
            admin=True,
            name="Admin D",
            email="admin_d@hospitald.com",
            password="pass1234",
            specialization="",
            contactInfo="1234567890",
        )
        hospitalStaff.objects.create(
            hospitalID=h4,
            admin=False,
            name="Doctor D",
            email="doctor_d@hospitald.com",
            password="pass1234",
            specialization="Forensic Pathology",
            contactInfo="1234567890",
        )

        # Adding user data
        u1 = user.objects.create(
            email="user1@example.com",
            name="User1",
            password="userpass1",
            username="user1",
            dob="1990-01-01",
            contactInfo="1234567890",
            proofOfIdentity="Proof1",
            address="Address1",
            securityQues="",
            securityAns="",
            bloodGroup="A+",
        )
        u2 = user.objects.create(
            email="user2@example.com",
            name="User2",
            password="userpass2",
            username="user2",
            dob="1990-01-01",
            contactInfo="1234567890",
            proofOfIdentity="Proof2",
            address="Address2",
            securityQues="",
            securityAns="",
            bloodGroup="B+",
        )
        u3 = user.objects.create(
            email="user3@example.com",
            name="User3",
            password="userpass3",
            username="user3",
            dob="1990-01-01",
            contactInfo="1234567890",
            proofOfIdentity="Proof3",
            address="Address3",
            securityQues="",
            securityAns="",
            bloodGroup="O+",
        )
        u4 = user.objects.create(
            email="user4@example.com",
            name="User4",
            password="userpass4",
            username="user4",
            dob="1990-01-01",
            contactInfo="1234567890",
            proofOfIdentity="Proof4",
            address="Address4",
            securityQues="",
            securityAns="",
            bloodGroup="AB+",
        )

        # Adding appointment Data
        a1 = appointment.objects.create(
            name="Vaccine",
            properties=json.dumps(
                {"type": "vaccine A", "dose_2": False, "date": datetime.now()},
                default=str,
            ),
        )
        a2 = appointment.objects.create(
            name="Vaccine",
            properties=json.dumps(
                {"type": "vaccine A", "dose_2": True, "date": datetime.now()},
                default=str,
            ),
        )
        a3 = appointment.objects.create(
            name="Blood test",
            properties=json.dumps(
                {"type": "Iron check", "dose_2": False, "date": datetime.now()},
                default=str,
            ),
        )
        a4 = appointment.objects.create(
            name="MRI",
            properties=json.dumps(
                {"type": "N/A", "dose_2": False, "date": datetime.now()}, default=str
            ),
        )

        # healthRecord data
        healthRecord.objects.create(
            doctorID=2,
            userID=u1,
            hospitalID=1,
            status="approved",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            appointmentId=a1,
            healthDocuments="",
        )
        healthRecord.objects.create(
            doctorID=2,
            userID=u2,
            hospitalID=2,
            status="rejected",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            appointmentId=a2,
            healthDocuments="",
        )
        healthRecord.objects.create(
            doctorID=3,
            userID=u3,
            hospitalID=3,
            status="approved",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            appointmentId=a3,
            healthDocuments="",
        )
        healthRecord.objects.create(
            doctorID=4,
            userID=u4,
            hospitalID=4,
            status="pending",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            appointmentId=a4,
            healthDocuments="",
        )

    def test_view_history(self):
        url = reverse("view_health_history")

        # request struct is empty
        request_struct = {}
        request = self.factory.get(url, request_struct)
        response = view_health_history(request)

        # only appointment name is passed
        request_struct = {"appointment_name": "Vaccine"}
        request = self.factory.get(url, request_struct)
        response = view_health_history(request)

        # appointment name and healthcare_worker are passed
        request_struct = {
            "appointment_name": "Vaccine",
            "healthcare_worker": "Doctor A",
        }
        request = self.factory.get(url, request_struct)
        response = view_health_history(request)

        # appointment name healthcare_worker and healthcare_facility are passed
        request_struct = {
            "appointment_name": "Vaccine",
            "healthcare_worker": "Doctor A",
            "healthcare_facility": "Hospital A",
        }
        request = self.factory.get(url, request_struct)
        response = view_health_history(request)

        # appointment name healthcare_worker, healthcare_facility and date are passed
        request_struct = {
            "appointment_name": "Vaccine",
            "healthcare_worker": "Doctor A",
            "healthcare_facility": "Hospital A",
            "date": "2024-03-08",
        }
        request = self.factory.get(url, request_struct)
        response = view_health_history(request)

        self.assertEqual(response.status_code, 200)

    def test_view_history_requests(self):
        url = reverse("view_requests")

        # appointment name healthcare_worker, healthcare_facility date and record_status are passed
        request_struct = {
            "appointment_name": "Vaccine",
            "healthcare_worker": "Doctor A",
            "healthcare_facility": "Hospital A",
            "date": "2024-03-08",
            "record_status": "approved",
        }
        request = self.factory.get(url, request_struct)
        response = view_health_history_requests(request)

        self.assertEqual(response.status_code, 200)


# Create your tests here.
