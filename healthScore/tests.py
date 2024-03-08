from django.test import TestCase, RequestFactory
from django.urls import reverse

from datetime import datetime
import json

from healthScore.models import (
    HealthRecord,
    Hospital,
    User,
    HospitalStaff,
    Appointment,
)
from healthScore.views import view_health_history


class viewHealthHistoryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Adding data to the Hospital table
        Hospital.objects.create(
            name="Hospital A",
            address="Address A",
            email="hospital_a@example.com",
            password="123456",
            contactInfo="123456781",
            status="approved",
        )
        Hospital.objects.create(
            name="Hospital B",
            address="Address B",
            email="hospital_b@example.com",
            password="123456",
            contactInfo="123456781",
            status="pending",
        )
        Hospital.objects.create(
            name="Hospital C",
            address="Address C",
            email="hospital_c@example.com",
            password="123456",
            contactInfo="123456781",
            status="rejected",
        )
        Hospital.objects.create(
            name="Hospital D",
            address="Address D",
            email="hospital_d@example.com",
            password="123456",
            contactInfo="123456781",
            status="pending",
        )

        # Adding hospitalStaff data
        HospitalStaff.objects.create(
            hospitalID=Hospital.objects.get(id=1),
            admin=True,
            name="Admin A",
            email="admin_a@hospitala.com",
            password="pass1234",
            specialization="",
            contactInfo="1234567890",
        )
        HospitalStaff.objects.create(
            hospitalID=Hospital.objects.get(id=1),
            admin=False,
            name="Doctor A",
            email="doctor_a@hospitala.com",
            password="pass1234",
            specialization="Anesthesiology",
            contactInfo="1234567890",
        )
        HospitalStaff.objects.create(
            hospitalID=Hospital.objects.get(id=2),
            admin=True,
            name="Admin B",
            email="admin_b@hospitalb.com",
            password="pass1234",
            specialization="",
            contactInfo="1234567890",
        )
        HospitalStaff.objects.create(
            hospitalID=Hospital.objects.get(id=2),
            admin=False,
            name="Doctor B",
            email="doctor_b@hospitalb.com",
            password="pass1234",
            specialization="Cardiology",
            contactInfo="1234567890",
        )
        HospitalStaff.objects.create(
            hospitalID=Hospital.objects.get(id=3),
            admin=True,
            name="Admin C",
            email="admin_c@hospitalc.com",
            password="pass1234",
            specialization="",
            contactInfo="1234567890",
        )
        HospitalStaff.objects.create(
            hospitalID=Hospital.objects.get(id=3),
            admin=False,
            name="Doctor C",
            email="doctor_c@hospitalc.com",
            password="pass1234",
            specialization="Dermatology",
            contactInfo="1234567890",
        )
        HospitalStaff.objects.create(
            hospitalID=Hospital.objects.get(id=4),
            admin=True,
            name="Admin D",
            email="admin_d@hospitald.com",
            password="pass1234",
            specialization="",
            contactInfo="1234567890",
        )
        HospitalStaff.objects.create(
            hospitalID=Hospital.objects.get(id=4),
            admin=False,
            name="Doctor D",
            email="doctor_d@hospitald.com",
            password="pass1234",
            specialization="Forensic Pathology",
            contactInfo="1234567890",
        )

        # Adding user data
        User.objects.create(
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
        User.objects.create(
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
        User.objects.create(
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
        User.objects.create(
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
        Appointment.objects.create(
            name="Vaccine",
            properties=json.dumps(
                {"type": "vaccine A", "dose_2": False, "date": datetime.now()},
                default=str,
            ),
        )
        Appointment.objects.create(
            name="Vaccine",
            properties=json.dumps(
                {"type": "vaccine A", "dose_2": True, "date": datetime.now()},
                default=str,
            ),
        )
        Appointment.objects.create(
            name="Blood test",
            properties=json.dumps(
                {"type": "Iron check", "dose_2": False, "date": datetime.now()},
                default=str,
            ),
        )
        Appointment.objects.create(
            name="MRI",
            properties=json.dumps(
                {"type": "N/A", "dose_2": False, "date": datetime.now()}, default=str
            ),
        )

        # healthRecord data
        HealthRecord.objects.create(
            doctorID=1,
            userID=User.objects.get(id=1),
            hospitalID=1,
            status="approved",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            appointmentId=Appointment.objects.get(id=1),
            healthDocuments="",
        )
        HealthRecord.objects.create(
            doctorID=2,
            userID=User.objects.get(id=2),
            hospitalID=2,
            status="rejected",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            appointmentId=Appointment.objects.get(id=2),
            healthDocuments="",
        )
        HealthRecord.objects.create(
            doctorID=3,
            userID=User.objects.get(id=3),
            hospitalID=3,
            status="approved",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            appointmentId=Appointment.objects.get(id=3),
            healthDocuments="",
        )
        HealthRecord.objects.create(
            doctorID=4,
            userID=User.objects.get(id=4),
            hospitalID=4,
            status="pending",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            appointmentId=Appointment.objects.get(id=4),
            healthDocuments="",
        )

    def test_view_history(self):
        url = reverse("view_health_history")

        request = self.factory.get(
            url,
            {
                "appointment_name": "test",
                "healthcare_worker": "test",
                "date": datetime.now(),
                "healthcare_facility": "test",
            },
        )
        request = self.factory.get(url)

        response = view_health_history(request)

        self.assertEqual(response.status_code, 200)


# Create your tests here.
