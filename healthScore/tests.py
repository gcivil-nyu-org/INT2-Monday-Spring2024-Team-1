from django.test import RequestFactory, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from datetime import datetime
import json

from healthScore.models import (
    HealthRecord,
    Hospital,
    User,
    HospitalStaff,
    Appointment,
)

from healthScore.views import (
    edit_user_info,
    homepage,
    registration,
    view_health_history,
    view_report,
    view_user_info,
    view_health_history_requests,
)


class viewHealthHistoryTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.factory = RequestFactory()

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
            password=make_password("userpass1"),
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
            password=make_password("userpass2"),
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
            password=make_password("userpass3"),
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
            password=make_password("userpass4"),
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
                {
                    "type": "vaccine A",
                    "dose_2": False,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                },
                default=str,
            ),
        )
        a2 = Appointment.objects.create(
            name="Vaccine",
            properties=json.dumps(
                {
                    "type": "vaccine A",
                    "dose_2": True,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                },
                default=str,
            ),
        )
        a3 = Appointment.objects.create(
            name="Blood test",
            properties=json.dumps(
                {
                    "type": "Iron check",
                    "dose_2": False,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                },
                default=str,
            ),
        )
        a4 = Appointment.objects.create(
            name="MRI",
            properties=json.dumps(
                {
                    "type": "N/A",
                    "dose_2": False,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                },
                default=str,
            ),
        )

        # healthRecord data
        hr1 = HealthRecord.objects.create(
            doctorID=1,
            userID=u1,
            hospitalID=1,
            status="approved",
            createdAt=datetime.now().strftime("%Y-%m-%d"),
            updatedAt=datetime.now().strftime("%Y-%m-%d"),
            appointmentId=a1,
            healthDocuments="",
        )
        hr2 = HealthRecord.objects.create(
            doctorID=2,
            userID=u2,
            hospitalID=2,
            status="approved",
            createdAt=datetime.now().strftime("%Y-%m-%d"),
            updatedAt=datetime.now().strftime("%Y-%m-%d"),
            appointmentId=a2,
            healthDocuments="",
        )
        hr3 = HealthRecord.objects.create(
            doctorID=3,
            userID=u3,
            hospitalID=3,
            status="approved",
            createdAt=datetime.now().strftime("%Y-%m-%d"),
            updatedAt=datetime.now().strftime("%Y-%m-%d"),
            appointmentId=a3,
            healthDocuments="",
        )
        hr4 = HealthRecord.objects.create(
            doctorID=4,
            userID=u4,
            hospitalID=4,
            status="pending",
            createdAt=datetime.now().strftime("%Y-%m-%d"),
            updatedAt=datetime.now().strftime("%Y-%m-%d"),
            appointmentId=a4,
            healthDocuments="",
        )

        print(hs1, hs2, hs3, hs4, hs5, hs6, hs7, hs8, hr1, hr2, hr3, hr4)

    def test_view_history(self):
        url = reverse("view_health_history")
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

    def test_view_user_info_pass(self):
        url = reverse("user_info")
        request = self.factory.get(
            url, data={"userId": "5"}, content_type="application/json"
        )
        request.user = self.user
        response = view_user_info(request)

        self.assertEqual(response.status_code, 200)

    def test_edit_user_info_exception(self):
        url = reverse("edit_user_info")
        request = self.factory.put(
            url,
            data={"userId": "6", "update": {"address": "test", "city": "test"}},
            content_type="application/json",
        )
        request.user = self.user
        response = edit_user_info(request)
        self.assertEqual(response.status_code, 500)

    def test_edit_user_info_pass(self):
        url = reverse("edit_user_info")
        request = self.factory.put(
            url,
            data={"userId": "1", "update": {"address": "test", "city": "test"}},
            content_type="application/json",
        )

        request.user = self.user
        response = edit_user_info(request)
        self.assertEqual(response.status_code, 200)

    def test_homepage(self):
        url = reverse("homepage")
        request = self.factory.get(url)
        response = homepage(request)

        self.assertEqual(response.status_code, 200)

    def test_view_history_requests(self):
        url = reverse("view_requests")
        # appointment name healthcare_worker, healthcare_facility date and record_status are passed
        request_struct = {
            "appointment_name": "Vaccine",
            "healthcare_worker": "Doctor A",
            "healthcare_facility": "Hospital B",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "record_status": "approved",
        }
        request = self.factory.get(url, request_struct)
        response = view_health_history_requests(request)
        self.assertEqual(response.status_code, 200)

    def test_login_fail(self):
        url = reverse("login")
        data = {"email": "user1@example.com", "password": "wrong password"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 500)

    def test_login_fail_wrong_method(self):
        url = reverse("login")
        data = {"email": "user1@example.com", "password": "userpass1"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 404)

    def test_login_success(self):
        url = reverse("login")
        data = {"email": "user1@example.com", "password": "userpass1"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

    def test_view_report(self):
        url = reverse("view_reports")
        request_struct = {"record_ids": [1, 2]}
        request = self.factory.post(url, request_struct)
        response = view_report(request)
        self.assertEqual(response.status_code, 200)

    def test_registration_pass(self):
        url = reverse("registration")
        request_struct = {
            "email": "test@test.com",
            "username": "testUser",
            "fullname": "test user",
            "dob": "1990-02-02",
            "gender": "male",
            "street_address": "123 foo bar, foo",
            "city": "NY",
            "state": "NY",
            "phone_number": "1235467890",
        }
        request = self.factory.post(url, request_struct)
        response = registration(request)
        self.assertEqual(
            response.status_code, 302
        )  # Since it's a redirect, status by default is 302 for sucesss

    def test_registration_not_post_method(self):
        url = reverse("registration")
        request_struct = {
            "email": "test@test.com",
            "username": "testUser",
            "fullname": "test user",
            "dob": "1990-02-02",
            "gender": "male",
            "street_address": "123 foo bar, foo",
            "city": "NY",
            "state": "NY",
            "phone_number": "1235467890",
        }
        request = self.factory.put(url, request_struct)
        response = registration(request)
        self.assertEqual(response.status_code, 404)

    def test_registration_user_email_exists_error(self):
        url = reverse("registration")
        request_struct = {
            "email": "user1@example.com",
            "username": "testUser",
            "fullname": "test user",
            "dob": "1990-02-02",
            "gender": "male",
            "street_address": "123 foo bar, foo",
            "city": "NY",
            "state": "NY",
            "phone_number": "1235467890",
        }
        request = self.factory.post(url, request_struct)
        response = registration(request)
        self.assertEqual(response.status_code, 500)

    def test_registration_user_username_exists_error(self):
        url = reverse("registration")
        request_struct = {
            "email": "test2@test2.com",
            "username": "user1",
            "fullname": "test user",
            "dob": "1990-02-02",
            "gender": "male",
            "street_address": "123 foo bar, foo",
            "city": "NY",
            "state": "NY",
            "phone_number": "1235467890",
        }
        request = self.factory.post(url, request_struct)
        response = registration(request)
        self.assertEqual(response.status_code, 500)


# Create your tests here.
