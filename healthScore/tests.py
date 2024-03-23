from django.test import RequestFactory, TransactionTestCase, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from datetime import datetime

from healthScore.models import (
    Hospital,
    User,
    HospitalStaff,
)

from healthScore.views import (
    edit_user_info,
    view_health_history,
    view_report,
    view_user_info,
    view_health_history_requests,
)


DATE_FORMAT = "%Y-%m-%d"


# views.py
class viewHealthHistoryTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.factory = RequestFactory()

        # # Adding data to the Hospital table
        # h1 = Hospital.objects.create(
        #     name="Hospital A",
        #     address="Address A",
        #     contactInfo="123456781",
        #     status="approved",
        # )
        # h2 = Hospital.objects.create(
        #     name="Hospital B",
        #     address="Address B",
        #     contactInfo="123456781",
        #     status="pending",
        # )
        # h3 = Hospital.objects.create(
        #     name="Hospital C",
        #     address="Address C",
        #     contactInfo="123456781",
        #     status="rejected",
        # )
        # h4 = Hospital.objects.create(
        #     name="Hospital D",
        #     address="Address D",
        #     contactInfo="123456781",
        #     status="pending",
        # )

        # Adding hospitalStaff data
        # hs1 = HospitalStaff.objects.create(
        #     hospitalID=h1,
        #     admin=True,
        #     name="Admin A",
        #     specialization="",
        #     contactInfo="1234567890",
        #     userID=0,
        # )
        # hs2 = HospitalStaff.objects.create(
        #     hospitalID=h1,
        #     admin=False,
        #     name="Doctor A",
        #     specialization="Anesthesiology",
        #     contactInfo="1234567890",
        #     userID=0,
        # )
        # hs3 = HospitalStaff.objects.create(
        #     hospitalID=h2,
        #     admin=True,
        #     name="Admin B",
        #     specialization="",
        #     contactInfo="1234567890",
        #     userID=0,
        # )
        # hs4 = HospitalStaff.objects.create(
        #     hospitalID=h2,
        #     admin=False,
        #     name="Doctor B",
        #     specialization="Cardiology",
        #     contactInfo="1234567890",
        #     userID=0,
        # )
        # hs5 = HospitalStaff.objects.create(
        #     hospitalID=h3,
        #     admin=True,
        #     name="Admin C",
        #     specialization="",
        #     contactInfo="1234567890",
        #     userID=0,
        # )
        # hs6 = HospitalStaff.objects.create(
        #     hospitalID=h3,
        #     admin=False,
        #     name="Doctor C",
        #     specialization="Dermatology",
        #     contactInfo="1234567890",
        #     userID=0,
        # )
        # hs7 = HospitalStaff.objects.create(
        #     hospitalID=h4,
        #     admin=True,
        #     name="Admin D",
        #     specialization="",
        #     contactInfo="1234567890",
        #     userID=0,
        # )
        # hs8 = HospitalStaff.objects.create(
        #     hospitalID=h4,
        #     admin=False,
        #     name="Doctor D",
        #     specialization="Forensic Pathology",
        #     contactInfo="1234567890",
        #     userID=0,
        # )

        # Adding user data
        u1 = User.objects.create_patient(
            email="user1@example.com",
            name="User1",
            password="userpass1",
            dob="1990-01-01",
            contactInfo="1234567890",
            proofOfIdentity="Proof1",
            address="Address1",
            securityQues="",
            securityAns="",
            bloodGroup="A+",
        )

        self.user = u1
        # u2 = User.objects.create_patient(
        #     email="user2@example.com",
        #     name="User2",
        #     password="userpass2",
        #     dob="1990-01-01",
        #     contactInfo="1234567890",
        #     proofOfIdentity="Proof2",
        #     address="Address2",
        #     securityQues="",
        #     securityAns="",
        #     bloodGroup="B+",
        # )
        # u3 = User.objects.create_patient(
        #     email="user3@example.com",
        #     name="User3",
        #     password="userpass3",
        #     dob="1990-01-01",
        #     contactInfo="1234567890",
        #     proofOfIdentity="Proof3",
        #     address="Address3",
        #     securityQues="",
        #     securityAns="",
        #     bloodGroup="O+",
        # )
        # u4 = User.objects.create_patient(
        #     email="user4@example.com",
        #     name="User4",
        #     password="userpass4",
        #     dob="1990-01-01",
        #     contactInfo="1234567890",
        #     proofOfIdentity="Proof4",
        #     address="Address4",
        #     securityQues="",
        #     securityAns="",
        #     bloodGroup="AB+",
        # )

        # Adding appointment Data
        # a1 = Appointment.objects.create(
        #     name="Vaccine",
        #     properties=json.dumps(
        #         {
        #             "type": "vaccine A",
        #             "dose_2": False,
        #             "date": datetime.now(),
        #         },
        #         default=str,
        #     ),
        # )
        # a2 = Appointment.objects.create(
        #     name="Vaccine",
        #     properties=json.dumps(
        #         {
        #             "type": "vaccine A",
        #             "dose_2": True,
        #             "date": datetime.now(),
        #         },
        #         default=str,
        #     ),
        # )
        # a3 = Appointment.objects.create(
        #     name="Blood test",
        #     properties=json.dumps(
        #         {
        #             "type": "Iron check",
        #             "dose_2": False,
        #             "date": datetime.now(),
        #         },
        #         default=str,
        #     ),
        # )
        # a4 = Appointment.objects.create(
        #     name="MRI",
        #     properties=json.dumps(
        #         {
        #             "type": "N/A",
        #             "dose_2": False,
        #             "date": datetime.now(),
        #         },
        #         default=str,
        #     ),
        # )

        # healthRecord data
        # hr1 = HealthRecord.objects.create(
        #     doctorID=1,
        #     userID=u1,
        #     hospitalID=1,
        #     status="approved",
        #     createdAt=datetime.now().strftime(DATE_FORMAT),
        #     updatedAt=datetime.now().strftime(DATE_FORMAT),
        #     appointmentId=a1,
        #     healthDocuments="",
        # )
        # hr2 = HealthRecord.objects.create(
        #     doctorID=2,
        #     userID=u2,
        #     hospitalID=2,
        #     status="approved",
        #     createdAt=datetime.now().strftime(DATE_FORMAT),
        #     updatedAt=datetime.now().strftime(DATE_FORMAT),
        #     appointmentId=a2,
        #     healthDocuments="",
        # )
        # hr3 = HealthRecord.objects.create(
        #     doctorID=3,
        #     userID=u3,
        #     hospitalID=3,
        #     status="approved",
        #     createdAt=datetime.now().strftime(DATE_FORMAT),
        #     updatedAt=datetime.now().strftime(DATE_FORMAT),
        #     appointmentId=a3,
        #     healthDocuments="",
        # )
        # hr4 = HealthRecord.objects.create(
        #     doctorID=4,
        #     userID=u4,
        #     hospitalID=4,
        #     status="pending",
        #     createdAt=datetime.now().strftime(DATE_FORMAT),
        #     updatedAt=datetime.now().strftime(DATE_FORMAT),
        #     appointmentId=a4,
        #     healthDocuments="",
        # )

        # print(hs1, hs2, hs3, hs4, hs5, hs6, hs7, hs8, hr1, hr2, hr3, hr4)

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
        request.user = self.user
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
        self.assertEqual(response.status_code, 200)

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

    def test_view_history_requests(self):
        url = reverse("view_requests")
        # appointment name healthcare_worker, healthcare_facility date and record_status are passed
        request_struct = {
            "appointment_name": "Vaccine",
            "healthcare_worker": "Doctor A",
            "healthcare_facility": "Hospital B",
            "date": datetime.now().strftime(DATE_FORMAT),
            "record_status": "approved",
        }
        request = self.factory.get(url, request_struct)
        request.user = self.user
        response = view_health_history_requests(request)
        self.assertEqual(response.status_code, 200)

    def test_view_report(self):
        url = reverse("view_reports")
        request_struct = {"record_ids": [1, 2]}
        request = self.factory.post(url, request_struct)
        response = view_report(request)
        self.assertEqual(response.status_code, 200)


class HomepageViewTest(TestCase):
    def test_homepage_view(self):
        response = self.client.get(reverse("homepage"))  # test the view
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "homepage.html")


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_patient(
            email="test@example.com", password="testpassword"
        )

    def test_login_view(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_post_request_valid_credentials(self):
        response = self.client.post(
            reverse("login"), {"email": "test@example.com", "password": "testpassword"}
        )
        self.assertRedirects(response, reverse("homepage"))

    def test_post_request_invalid_credentials(self):
        response = self.client.post(
            reverse("login"), {"email": "test@example.com", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Invalid email or password. Please try again.", response.content.decode()
        )


class RegistrationViewTest(TestCase):
    def setUp(self):
        self.patient = User.objects.create_patient(
            email="patient@example.com",
            name="Patient 1",
            password="patientpass",
        )

        self.admin = User.objects.create_staff(
            email="admin@example.com",
            name="Admin 1",
            password="adminpass",
        )

        self.healthcareWorker = User.objects.create_healthcare_worker(
            email="doctor@example.com",
            name="Doctor 1",
            password="doctorpass",
        )

        self.hospital = Hospital.objects.create(
            name="Hospital A",
            address="Address A",
            contactInfo="1234567890",
        )

    def test_registration_view(self):
        response = self.client.get(reverse("registration"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration.html")

    def test_post_request_patient_exists(self):
        response = self.client.post(
            reverse("registration"),
            {"email": "patient@example.com", "password": "testpassword"},
        )
        user = User.objects.get(email="patient@example.com")
        self.assertEqual(user.email, "patient@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "A patient account already exists with this email",
            response.content.decode(),
        )

    def test_post_request_admin_exists(self):
        response = self.client.post(
            reverse("registration"),
            {"email": "admin@example.com", "password": "testpassword"},
        )
        user = User.objects.get(email="admin@example.com")
        self.assertEqual(user.email, "admin@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "An admin account already exists with this email",
            response.content.decode(),
        )

    def test_post_request_healthcare_worker_exists(self):
        response = self.client.post(
            reverse("registration"),
            {"email": "doctor@example.com", "password": "testpassword"},
        )
        user = User.objects.get(email="doctor@example.com")
        self.assertEqual(user.email, "doctor@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "A healthcare worker account already exists with this email",
            response.content.decode(),
        )

    def test_post_request_new_user_registered(self):
        response = self.client.post(
            reverse("registration"),
            {
                "email": "newuser@example.com",
                "password": "newpassword",
                "fullname": "New User",
                "gender": "female",
                "phone_number": "0000000000",
                "street_address:": "1 High St",
                "city": "Jersey City",
                "state": "NJ",
                "role": "User",
                "contactInfo": "1234567890",
                "identity_proof": "Proof.pdf",
            },
        )
        user = User.objects.get(email="newuser@example.com")
        self.assertEqual(user.email, "newuser@example.com")
        self.assertRedirects(response, reverse("homepage"))

    def test_post_request_new_admin_registered(self):
        response = self.client.post(
            reverse("registration"),
            {
                "role": "Healthcare Admin",
                "email": "newadmin@example.com",
                "password": "newpassword",
                "fullname": "New Admin",
                "contactInfo": "1234567890",
                "hospital_name": "Hospital B",
                "facility_street_address": "24 St",
                "facility_city": "Brooklyn",
                "facility_state": "NY",
                "facility_zipcode": "11201",
            },
        )
        user = User.objects.get(email="newadmin@example.com")
        self.assertEqual(user.email, "newadmin@example.com")
        self.assertRedirects(response, reverse("homepage"))


# class AddRecordViewTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_patient(
#             email="test@example.com", password="testpassword"
#         )

#     def test_add_record_view(self):
#         response = self.client.get(reverse("new_health_record"))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "record_submit.html")

#     def test_add_new_record_success(self):
#         response = self.client.post(
#             reverse("new_health_record"), {
#                 "hospitalID": 1,
#                 "doctorId": 1,
#                 "appointmentType": "eye"
#             }
#         )


# models.py
class CustomUserManagerTest(TestCase):
    def test_create_patient(self):
        User = get_user_model()
        email = "test@example.com"
        password = "testpassword"
        user = User.objects.create_patient(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.is_patient)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password(password))

    def test_create_staff(self):
        User = get_user_model()
        email = "test@example.com"
        password = "testpassword"
        user = User.objects.create_staff(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertFalse(user.is_patient)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.check_password(password))

    def test_create_patient_missing_email(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_patient(email=None, password="testpassword")


class UserTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="test@exmaple.com",
            password="password",
            name="Test User",
        )

    def test_get_full_name(self):
        full_name = self.user.get_full_name()
        self.assertEqual(full_name, "Test User")


class HospitalStaffTests(TestCase):

    def setUp(self):
        self.hospital = Hospital.objects.create(name="Test Hospital")
        self.user = User.objects.create(
            email="doctor@example.com",
            password="testpass123",
        )
        self.hospital_staff = HospitalStaff.objects.create(
            hospitalID=self.hospital,
            admin=False,
            name="Test Doctor",
            specialization="Cardiology",
            contactInfo="1234567890",
            userID=self.user.id,
        )
        self.url = reverse("get_facility_doctors")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
