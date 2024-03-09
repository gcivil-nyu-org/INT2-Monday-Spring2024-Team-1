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
from healthScore.views import edit_user_info, view_health_history, view_user_info


class viewHealthHistoryTestCase(TestCase):
    def setUp(self):
        # print("SOMETHING")
        self.factory = RequestFactory()
        # self.user = user.objects.create_user(
        #     username='test', email='test@test.com', password='my_secret')
        # Adding data to the Hospital table
        h1 = Hospital.objects.create(
            name="Hospital A",
            address="Address A",
            email="hospital_a@example.com",
            password="123456",
            contactInfo="123456781",
            status="approved",
        )
        


        h2 = Hospital.objects.create(
            name="Hospital B",
            address="Address B",
            email="hospital_b@example.com",
            password="123456",
            contactInfo="123456781",
            status="pending",
        )
        h3 = Hospital.objects.create(
            name="Hospital C",
            address="Address C",
            email="hospital_c@example.com",
            password="123456",
            contactInfo="123456781",
            status="rejected",
        )
        h4 = Hospital.objects.create(
            name="Hospital D",
            address="Address D",
            email="hospital_d@example.com",
            password="123456",
            contactInfo="123456781",
            status="pending",
        )

        # Adding hospitalStaff data
        hs1 = HospitalStaff.objects.create(
            hospitalID=h1,
            admin=True,
            name="Admin A",
            email="admin_a@hospitala.com",
            password="pass1234",
            specialization="",
            contactInfo="1234567890",
        )
        hs2 = HospitalStaff.objects.create(
            hospitalID=h1,
            admin=False,
            name="Doctor A",
            email="doctor_a@hospitala.com",
            password="pass1234",
            specialization="Anesthesiology",
            contactInfo="1234567890",
        )
        hs3 = HospitalStaff.objects.create(
            hospitalID=h2,
            admin=True,
            name="Admin B",
            email="admin_b@hospitalb.com",
            password="pass1234",
            specialization="",
            contactInfo="1234567890",
        )
        hs4 = HospitalStaff.objects.create(
            hospitalID=h2,
            admin=False,
            name="Doctor B",
            email="doctor_b@hospitalb.com",
            password="pass1234",
            specialization="Cardiology",
            contactInfo="1234567890",
        )
        hs5 = HospitalStaff.objects.create(
            hospitalID=h3,
            admin=True,
            name="Admin C",
            email="admin_c@hospitalc.com",
            password="pass1234",
            specialization="",
            contactInfo="1234567890",
        )
        hs6 = HospitalStaff.objects.create(
            hospitalID=h3,
            admin=False,
            name="Doctor C",
            email="doctor_c@hospitalc.com",
            password="pass1234",
            specialization="Dermatology",
            contactInfo="1234567890",
        )
        hs7 = HospitalStaff.objects.create(
            hospitalID=h4,
            admin=True,
            name="Admin D",
            email="admin_d@hospitald.com",
            password="pass1234",
            specialization="",
            contactInfo="1234567890",
        )
        hs8 = HospitalStaff.objects.create(
            hospitalID=h4,
            admin=False,
            name="Doctor D",
            email="doctor_d@hospitald.com",
            password="pass1234",
            specialization="Forensic Pathology",
            contactInfo="1234567890",
        )

        # Adding user data
        u1 = User.objects.create(
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
        
        self.user = u1
        u2 = User.objects.create(
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
        u3 = User.objects.create(
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
        u4 = User.objects.create(
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
        a1 = Appointment.objects.create(
            name="Vaccine",
            properties=json.dumps(
                {"type": "vaccine A", "dose_2": False, "date": datetime.now()},
                default=str,
            ),
        )
        a2 = Appointment.objects.create(
            name="Vaccine",
            properties=json.dumps(
                {"type": "vaccine A", "dose_2": True, "date": datetime.now()},
                default=str,
            ),
        )
        a3 = Appointment.objects.create(
            name="Blood test",
            properties=json.dumps(
                {"type": "Iron check", "dose_2": False, "date": datetime.now()},
                default=str,
            ),
        )
        a4 = Appointment.objects.create(
            name="MRI",
            properties=json.dumps(
                {"type": "N/A", "dose_2": False, "date": datetime.now()}, default=str
            ),
        )

        # healthRecord data
        hr1 = HealthRecord.objects.create(
            doctorID=1,
            userID=u1,
            hospitalID=1,
            status="approved",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            appointmentId=a1,
            healthDocuments="",
        )
        hr2 = HealthRecord.objects.create(
            doctorID=2,
            userID=u2,
            hospitalID=2,
            status="rejected",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            appointmentId=a2,
            healthDocuments="",
        )
        hr3 = HealthRecord.objects.create(
            doctorID=3,
            userID=u3,
            hospitalID=3,
            status="approved",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            appointmentId=a3,
            healthDocuments="",
        )
        hr4 = HealthRecord.objects.create(
            doctorID=4,
            userID=u4,
            hospitalID=4,
            status="pending",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            appointmentId=a4,
            healthDocuments="",
        )

        print(hs1, hs2, hs3, hs4, hs5, hs6, hs7, hs8, hr1, hr2, hr3, hr4)

    def test_view_history(self):
        url = reverse("view_health_history")

        # Update below request with user ID/user info
        request = self.factory.get(
            url,
            {
                "appointment_name": "Vaccine",
                "healthcare_worker": "Doctor A",
                "date":"2024-03-07",
                "healthcare_facility": "Hospital A",
            },
        )
        # request = self.factory.get(url)
        response = view_health_history(request)
        self.assertEqual(response.status_code, 200)


    def test_view_user_info_pass(self):
        url = reverse("user_info")
        request = self.factory.get(
            url, data={"userId": "5"}, content_type="application/json"
        )
        request.user = self.user
        response = view_user_info(request)

        # Update below assetion to 500 once the userInfo html gets pushed
        self.assertEqual(response.status_code, 200)

    
    
    def test_edit_user_info_exception(self):
        url = reverse("edit_user_info")
        request = self.factory.put(
            url,
            data={"userId": "6", "update": {"address": "test", "city": "test"}},
            content_type="application/json",
        )

        response = edit_user_info(request)

        # Update below assetion to 500 once the userInfo html gets pushed
        self.assertEqual(response.status_code, 500)

    def test_edit_user_info_pass(self):
        url = reverse("edit_user_info")
        request = self.factory.put(
            url,
            data={"userId": "6", "update": {"address": "test", "city": "test"}},
            content_type="application/json",
        )

        response = edit_user_info(request)

        # Update below assetion to 500 once the userInfo html gets pushed
        self.assertEqual(response.status_code, 200)


# Create your tests here.
