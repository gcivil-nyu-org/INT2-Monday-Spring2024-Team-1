from django.test import RequestFactory, TransactionTestCase, TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import HttpRequest
import os
from django.core import mail
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile

from datetime import datetime
import json

from healthScore.models import (
    HealthRecord,
    Hospital,
    User,
    HospitalStaff,
    Appointment,
    Post,
    HealthHistoryAccessRequest,
    Comment,
)

from healthScore.file_upload import file_upload

from healthScore.profile_view import edit_user_info, view_user_info

from healthScore.patient_view_records import (
    view_health_history_requests,
    view_report,
    get_record,
    view_health_history,
    view_health_history_doc,
)

from healthScore.patient_submit_health_record import (
    get_doctors,
    get_edit,
    edit_health_record_view,
    add_health_record_view,
    record_sent_view,
)

from healthScore.healthcare_data import (
    add_healthcare_staff,
    deactivate_healthcare_staff,
    activate_healthcare_staff,
)

from healthScore.community_data import (
    view_all_posts,
    view_post,
    create_post,
    edit_post,
    delete_post,
    create_comments,
    delete_comment,
)

from healthScore.homepage_and_auth import (
    user_dashboard,
)

from healthScore.external_health_request_access import (
    request_health_history,
    view_health_history_access_requests,
)

from healthScore.admin_view_user_healthrecords import (
    admin_view_health_history_requests,
    get_admin_edit,
)

DATE_FORMAT = "%Y-%m-%d"


# views.py
class viewHealthHistoryTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_patient(
            email="user1@example.com",
            name="User1",
            password="userpass1",
            dob=datetime.strptime("1990-01-01", "%Y-%m-%d"),
            contactInfo="1234567890",
            proofOfIdentity="Proof1",
            address="Address1",
            securityQues="",
            securityAns="",
            bloodGroup="A+",
        )
        self.appointment = Appointment.objects.create(
            name="Eye Test",
            properties=json.dumps(
                {
                    "cylindrical_power_right": 1.25,
                    "cylindrical_power_left": 0.75,
                    "spherical_power_left": -2.00,
                    "spherical_power_right": -1.50,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                }
            ),
        )
        self.health_record = HealthRecord.objects.create(
            doctorID=1,
            userID=self.user,
            hospitalID=1,
            status="approved",
            appointmentId=self.appointment,
        )
        self.hospital = Hospital.objects.create(
            name="Hospital A",
            address="Address A",
            contactInfo="1234567890",
        )
        self.hospital_staff = HospitalStaff.objects.create(
            hospitalID=self.hospital,
            admin=False,
            name="Doctor A",
            specialization="Cardiology",
            contactInfo="1234567890",
            userID=self.user.id,
        )

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
        request = self.factory.post(
            url,
            data={"userId": "6", "update": {"address": "test", "city": "test"}},
            content_type="application/json",
        )
        request.user = self.user
        response = edit_user_info(request)
        self.assertEqual(response.status_code, 200)

    def test_edit_user_info_pass(self):
        url = reverse("edit_user_info")
        request = self.factory.post(
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
        request = HttpRequest()
        request.method = "GET"  # Set the HTTP method to GET
        request.path = url
        request.user = self.user
        request.GET["appointment_name"] = "Vaccine"
        request.GET["healthcare_worker"] = "Doctor A"
        request.GET["healthcare_facility"] = "Hospital B"
        request.GET["date"] = datetime.now().strftime(DATE_FORMAT)
        request.GET["record_status"] = "approved"
        response = view_health_history_requests(request)
        self.assertEqual(response.status_code, 200)

    def test_view_report(self):
        url = reverse("view_reports")
        request_struct = {"record_ids": [self.health_record.id]}
        request = self.factory.post(url, request_struct)
        request.user = self.user
        response = view_report(request)
        self.assertEqual(response.status_code, 200)

    def test_get_doctors(self):
        request = HttpRequest()
        request.GET["hos_id"] = "1"
        response = get_doctors(request, 1)
        self.assertEqual(response.status_code, 200)

    def test_get_records(self):
        request = HttpRequest()
        request.GET["rec_id"] = "1"
        response = get_record(request, 1)
        self.assertEqual(response.status_code, 200)

    def test_new_health_record_sent(self):
        request = HttpRequest()
        request.user = self.user
        response = record_sent_view(request)
        self.assertEqual(response.status_code, 200)

    def test_get_edit(self):
        url = reverse("get_edit", args=[1])
        request = HttpRequest()
        request.path = url
        request.user = self.user
        request.GET["rec_id"] = "1"

        response = get_edit(request, 1)
        self.assertEqual(response.status_code, 200)

    def test_add_health_record_view(self):
        url = reverse("new_health_record")
        request = HttpRequest()
        request.path = url
        request.user = self.user
        request.method = "POST"
        request.POST["hospitalID"] = "1"
        request.POST["doctorId"] = "1"
        request.POST["appointmentType"] = "blood_test"
        request.POST["type"] = "Covid"

        response = add_health_record_view(request)
        self.assertEqual(response.status_code, 302)

    def test_add_health_record_view_else(self):
        url = reverse("new_health_record")
        request = HttpRequest()
        request.path = url
        request.user = self.user
        request.method = "GET"

        response = add_health_record_view(request)
        self.assertEqual(response.status_code, 200)

    def test_edit_health_record_view(self):
        url = reverse("edit_record")
        request = HttpRequest()
        request.path = url
        request.method = "POST"

        request.POST["recordId"] = "1"
        request.POST["appointmentId"] = "1"
        request.POST["appointmentType"] = "blood_test"
        request.POST["appointmentProperties"] = {"type": "Covid"}
        request.POST["doctorId"] = "1"
        request.POST["hospitalID"] = "1"

        request.user = self.user
        response = edit_health_record_view(request)
        self.assertEqual(response.status_code, 302)


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
        self.assertRedirects(response, reverse("user_dashboard"))

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


class RecordSentView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_patient(
            email="test@example.com", password="testpassword"
        )

    def test_record_sent_view(self):
        request = self.factory.get(reverse("new_health_record_sent"))
        request.user = self.user
        response = record_sent_view(request)
        self.assertEqual(response.status_code, 200)


class AddRecordViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_patient(
            email="test@example.com", password="testpassword"
        )

    def test_add_record_view(self):
        request = self.factory.get(reverse("new_health_record"))
        request.user = self.user
        response = add_health_record_view(request)
        self.assertEqual(response.status_code, 200)

    def test_add_new_record_success(self):
        request = self.factory.post(
            reverse("new_health_record"),
            {
                "hospitalID": 1,
                "doctorId": 1,
                "appointmentType": "eye",
                "cylindrical_power_right": 1.25,
                "cylindrical_power_left": 0.75,
                "spherical_power_left": -2.00,
                "spherical_power_right": -1.50,
                "date": "2024-04-15",
            },
        )
        request.user = self.user
        response = add_health_record_view(request)
        self.assertEqual(response.status_code, 302)


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
        self.factory = RequestFactory()
        self.hospital = Hospital.objects.create(name="Test Hospital")
        self.user = User.objects.create(
            email="admin@example.com", password="testpass123", is_staff=1, is_active=1
        )
        self.patient = User.objects.create(
            id=1,
            email="patient@example.com",
            password="testpass123",
            is_patient=1,
            is_active=1,
        )
        self.doctor = User.objects.create(
            id=2,
            email="doctor@example.com",
            password="testpass123",
            is_healthcare_worker=1,
            is_active=1,
        )
        self.hospital_staff = HospitalStaff.objects.create(
            hospitalID=self.hospital,
            admin=False,
            name="Test Doctor",
            specialization="Cardiology",
            contactInfo="1234567890",
            userID=self.doctor.id,
        )
        self.url = reverse("get_facility_doctors")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_activate_healthcare_staff_error(self):
        request = self.factory.put(
            reverse("activate_healthcare_staff"),
            data={"user_id": 1},
            content_type="application/json",
        )

        request.user = self.user
        response = activate_healthcare_staff(request)
        self.assertEqual(response.status_code, 400)

    def test_activate_healthcare_staff_pass(self):
        request = self.factory.put(
            reverse("activate_healthcare_staff"),
            data={"user_id": 2},
            content_type="application/json",
        )

        request.user = self.user
        response = activate_healthcare_staff(request)
        self.assertEqual(response.status_code, 200)

    def test_deactivate_healthcare_staff_error(self):
        request = self.factory.put(
            reverse("deactivate_healthcare_staff"),
            data={"user_id": 1},
            content_type="application/json",
        )

        request.user = self.user
        response = deactivate_healthcare_staff(request)
        self.assertEqual(response.status_code, 200)

    def test_deactivate_healthcare_staff_pass(self):
        request = self.factory.put(
            reverse("deactivate_healthcare_staff"),
            data={"user_id": 2},
            content_type="application/json",
        )

        request.user = self.user
        response = deactivate_healthcare_staff(request)
        self.assertEqual(response.status_code, 200)


class CommunityTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user1 = User.objects.create(
            email="patient@example.com",
            name="User 1",
            password="patientpass",
        )
        self.post = Post.objects.create(
            title="Test Post", description="Test Description", user=self.user1
        )

        self.comment = Comment.objects.create(
            post=self.post, content="Test a comment", commenter=self.user1
        )

    def test_view_all_posts(self):
        request = self.factory.get(reversed("all_posts"))
        request.user = self.user1
        response = view_all_posts(request)
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        request = self.factory.post(
            reverse("create_post"),
            {"title": "Test Title", "description": "Test Description"},
        )
        request.user = self.user1
        response = create_post(request)
        self.assertEqual(response.status_code, 302)

    def test_view_post(self):
        request = self.factory.get(
            reverse("view_post", kwargs={"post_id": self.post.id})
        )
        request.user = self.user1
        response = view_post(request, post_id=self.post.id)
        self.assertEqual(response.status_code, 200)

    def test_create_comments(self):
        comment_data = {"content": "Test Comment"}
        request = self.factory.post(
            reverse("create_comments", kwargs={"post_id": self.post.id}), comment_data
        )
        request.user = self.user1
        response = create_comments(request, post_id=self.post.id)
        self.assertEqual(response.status_code, 302)

    def test_delete_post(self):
        request = self.factory.get(reverse("delete_post", args=[self.post.id]))
        request.user = self.user1
        old_count = Post.objects.count()
        response = delete_post(request, post_id=self.post.id)
        self.assertEqual(response.status_code, 302)
        new_count = Post.objects.count()
        self.assertEqual(old_count - new_count, 1)

    def test_delete_comment(self):
        request = self.factory.get(reverse("delete_comment", args=[self.comment.id]))
        request.user = self.user1
        old_count = Comment.objects.count()
        response = delete_comment(request, comment_id=self.comment.id)
        self.assertEqual(response.status_code, 302)
        new_count = Comment.objects.count()
        self.assertEqual(old_count - new_count, 1)

    def test_edit_post(self):
        new_post = {"title": "Updated Title", "description": "Updated Description"}
        request = self.factory.post(reverse("edit_post", args=[self.post.id]), new_post)
        request.user = self.user1
        response = edit_post(request, post_id=self.post.id)
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Title")
        self.assertEqual(self.post.description, "Updated Description")


class AddHealthcareStaffTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        h1 = Hospital.objects.create(
            id=1,
            name="Hospital A",
            address="Address A",
            contactInfo="1234567890",
        )

        User.objects.create_patient(
            id=1,
            email="patient@example.com",
            name="Patient 1",
            password="patientpass",
            is_patient=1,
        )

        self.admin = User.objects.create_staff(
            id=2,
            email="admin@example.com",
            name="Admin 1",
            password="adminpass",
            is_staff=1,
        )

        User.objects.create_healthcare_worker(
            id=3,
            email="doctor@example.com",
            name="Doctor 1",
            password="doctorpass",
            is_healthcare_worker=1,
        )

        HospitalStaff.objects.create(
            hospitalID=h1,
            admin=True,
            userID=2,
        )

    def test_post_request_patient_exists(self):
        request = self.factory.post(
            reverse("add_healthcare_staff"),
            {
                "email": "patient@example.com",
                "fullname": "New Admin",
                "contactInfo": "9746352632",
                "specialization": "",
                "is_admin": 1,
            },
        )
        request.user = self.admin

        response = add_healthcare_staff(request)

        self.assertIn(
            "A patient account already exists with this email",
            response.content.decode(),
        )

    def test_post_request_admin_exists(self):
        request = self.factory.post(
            reverse("add_healthcare_staff"),
            {
                "email": "admin@example.com",
                "fullname": "New Admin",
                "contactInfo": "9746352632",
                "specialization": "",
                "is_admin": 1,
            },
        )
        request.user = self.admin

        response = add_healthcare_staff(request)

        self.assertIn(
            "An admin account already exists with this email",
            response.content.decode(),
        )

    def test_post_request_healthcare_worker_exists(self):
        request = self.factory.post(
            reverse("add_healthcare_staff"),
            {
                "email": "doctor@example.com",
                "fullname": "New Admin",
                "contactInfo": "9746352632",
                "specialization": "",
                "is_admin": 1,
            },
        )
        request.user = self.admin

        response = add_healthcare_staff(request)

        self.assertIn(
            "A healthcare worker account already exists with this email",
            response.content.decode(),
        )

    def test_valid_post_request(self):
        request = self.factory.post(
            reverse("add_healthcare_staff"),
            {
                "email": "newadmin@example.com",
                "fullname": "New Admin",
                "contactInfo": "9746352632",
                "specialization": "",
                "is_admin": 1,
            },
        )
        request.user = self.admin

        response = add_healthcare_staff(request)

        self.assertEqual(response.status_code, 302)


class RequestHealthHistoryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.patient = User.objects.create_patient(
            id=1,
            email="patient@example.com",
            name="Patient 1",
            password="patientpass",
            is_patient=1,
            dob="1997-12-30",
        )

        self.admin = User.objects.create_staff(
            id=2,
            email="admin@example.com",
            name="Admin 1",
            password="adminpass",
            is_staff=1,
            dob="1997-12-30",
        )

    def test_post_request_patient_does_not_exist(self):
        request = self.factory.post(
            reverse("request_health_history"),
            {
                "requestorName": "Aman Jain",
                "requestorEmail": "requestor@gmail.com",
                "purpose": "For onboarding process",
                "userEmail": "abcd@gmail.com",
                "dob": "1997-12-28",
            },
        )

        response = request_health_history(request)
        self.assertIn(
            "No user account exists with these details",
            response.content.decode(),
        )

    def test_post_request_admin_email_exists(self):
        request = self.factory.post(
            reverse("request_health_history"),
            {
                "requestorName": "Aman Jain",
                "requestorEmail": "requestor@gmail.com",
                "purpose": "For onboarding process",
                "userEmail": "admin@example.com",
                "dob": "1997-12-30",
            },
        )

        response = request_health_history(request)
        self.assertIn(
            "No user account exists with these details",
            response.content.decode(),
        )

    def test_valid_post_request(self):
        request = self.factory.post(
            reverse("request_health_history"),
            {
                "requestorName": "Aman Jain",
                "requestorEmail": "requestor@gmail.com",
                "purpose": "For onboarding process",
                "userEmail": "patient@example.com",
                "dob": "1997-12-30",
            },
        )

        response = request_health_history(request)
        self.assertEqual(response.status_code, 302)


class ViewHealthHistoryAccessTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_patient(
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

        HealthHistoryAccessRequest.objects.create(
            requestorName="Test Requestor",
            requestorEmail="testrequestor@gmail.com",
            purpose="For onboarding process",
            userID=self.user,
        )

    def test_view_health_history_access_requests(self):
        url = reverse("view_health_history_access_requests")
        request = self.factory.get(url)
        request.user = self.user
        response = view_health_history_access_requests(request)
        self.assertEqual(response.status_code, 200)

    def test_wrong_request_method(self):
        url = reverse("view_health_history_access_requests")
        request = self.factory.put(url)
        request.user = self.user
        response = view_health_history_access_requests(request)
        self.assertEqual(response.status_code, 401)


class UpdateHealthHistoryAccessRequestStatusTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_patient(
            email="test@example.com", password="password123", dob=datetime.now().date()
        )
        self.client.login(email="test@example.com", password="password123")
        # Create test health history access requests
        self.hhars = [
            HealthHistoryAccessRequest.objects.create(
                userID=self.user, status="pending"
            )
            for _ in range(2)
        ]

    def test_send_approval_emails(self):
        url = reverse("send_approval_emails")
        data = {
            "emails": ["test1@example.com", "test2@example.com"],
            "requestIds": [hhar.id for hhar in self.hhars],
        }

        response = self.client.post(url, data, content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 2)
        for hhar in self.hhars:
            hhar.refresh_from_db()
            self.assertEqual(hhar.status, "approved")

    def test_send_rejection_emails(self):
        url = reverse("send_reject_emails")
        data = {
            "emails": ["test3@example.com", "test4@example.com"],
            "requestIds": [hhar.id for hhar in self.hhars],
        }

        response = self.client.post(url, data, content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 2)
        for hhar in self.hhars:
            hhar.refresh_from_db()
            self.assertEqual(hhar.status, "rejected")


# Testing the function for file upload directly. So the 'url' used is relevant
class TestFileUpload(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(
            email="myUser@example.com",
            password="testpass123",
            is_patient=1,
            is_active=1,
        )
        os.environ["AWS_ACCESS_KEY_ID"] = "RandomKey"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "RandomSecretKey"
        os.environ["AWS_S3_REGION_NAME"] = "RandomRegion"

    @patch("boto3.resource")
    def test_file_upload_profile_pic(self, mock_boto3_resource):
        mock_s3_resource = mock_boto3_resource.return_value
        mock_bucket = mock_s3_resource.Bucket.return_value

        mock_bucket.upload_file.return_value = None

        file_path = "healthScore/static/mock-data.txt"

        with open(file_path, "rb") as f:
            file_data = f.read()
            file = SimpleUploadedFile(
                "example.txt", file_data, content_type="text/plain"
            )

        request = self.factory.post(
            reverse("edit_user_info"),
            data={"profile_picture": file},
            format="multipart",
        )
        request.user = self.user

        # Checking number of urls returned below because once the "Actual" keys are picked up from the pipeline, the url format changes
        url = [file_upload(request, "userProfile")]
        mock_bucket.upload_file.assert_called_once()
        self.assertEqual(
            len(url),
            1,
        )

    @patch("boto3.resource")
    def test_file_upload_medical_document(self, mock_boto3_resource):
        mock_s3_resource = mock_boto3_resource.return_value
        mock_bucket = mock_s3_resource.Bucket.return_value

        mock_bucket.upload_file.return_value = None

        file_path = "healthScore/static/mock-data.txt"

        with open(file_path, "rb") as f:
            file_data = f.read()
            file = SimpleUploadedFile(
                "example.txt", file_data, content_type="text/plain"
            )

        request = self.factory.post(
            reverse("edit_user_info"),
            data={"medical_document": file},
            format="multipart",
        )
        request.user = self.user

        # Checking number of urls returned below because once the "Actual" keys are picked up from the pipeline, the url format changes
        url = [file_upload(request, "medicalHistory")]
        mock_bucket.upload_file.assert_called_once()

        self.assertEqual(
            len(url),
            1,
        )

    @patch("boto3.resource")
    def test_file_upload_identity_proof(self, mock_boto3_resource):
        mock_s3_resource = mock_boto3_resource.return_value
        mock_bucket = mock_s3_resource.Bucket.return_value

        mock_bucket.upload_file.return_value = None

        file_path = "healthScore/static/mock-data.txt"

        with open(file_path, "rb") as f:
            file_data = f.read()
            file = SimpleUploadedFile(
                "example.txt", file_data, content_type="text/plain"
            )

        request = self.factory.post(
            reverse("edit_user_info"),
            data={"identity_proof": file, "email": "myUser@example.com"},
            format="multipart",
        )

        # Checking number of urls returned below because once the "Actual" keys are picked up from the pipeline, the url format changes
        url = [file_upload(request, "identityProof")]
        mock_bucket.upload_file.assert_called_once()
        self.assertEqual(
            len(url),
            1,
        )

    # Test Upload failure and exception blocks
    def test_file_upload_failure(self):
        request = self.factory.post(
            reverse("edit_user_info"),
        )
        url = file_upload(request, "TEST")
        self.assertEqual(url, "")

    def test_file_upload_profile_pic_failure_exception(self):
        file_path = "healthScore/static/mock-data.txt"

        with open(file_path, "rb") as f:
            file_data = f.read()
            file = SimpleUploadedFile(
                "example.txt", file_data, content_type="text/plain"
            )

        request = self.factory.post(
            reverse("edit_user_info"),
            data={"profile_picture": file},
            format="multipart",
        )

        url = file_upload(request, "userProfile")
        self.assertEqual(url, "")

    def test_file_upload_identity_proof_failure_exception(self):
        file_path = "healthScore/static/mock-data.txt"

        with open(file_path, "rb") as f:
            file_data = f.read()
            file = SimpleUploadedFile(
                "example.txt", file_data, content_type="text/plain"
            )

        request = self.factory.post(
            reverse("edit_user_info"), data={"identity_proof": file}, format="multipart"
        )

        url = file_upload(request, "identityProof")
        self.assertEqual(url, "")


class TestRequestDecision(TestCase):
    def setUp(self):
        # self.factory = RequestFactory()
        self.hospital = Hospital.objects.create(name="Test Hospital")
        self.user = User.objects.create_patient(
            email="user1@example.com",
            name="User1",
            password="userpass1",
        )
        self.client.login(email="user1@example.com", password="userpass1")
        self.doctor = User.objects.create(
            # id=2,
            email="doctor@example.com",
            password="testpass123",
            is_healthcare_worker=True,
            is_active=True,
        )

        self.appointment = Appointment.objects.create(
            name="Eye Test",
            properties=json.dumps(
                {
                    "cylindrical_power_right": 1.25,
                    "cylindrical_power_left": 0.75,
                    "spherical_power_left": -2.00,
                    "spherical_power_right": -1.50,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                }
            ),
        )
        self.health_record = HealthRecord.objects.create(
            doctorID=self.doctor.id,
            userID=self.user,
            hospitalID=self.hospital.id,
            appointmentId=self.appointment,
        )

    def test_approval(self):
        url = reverse("update_request_status")
        self.user = self.doctor
        response = self.client.post(
            url, {"recordID": self.health_record.id, "status": "approved"}
        )
        self.health_record.refresh_from_db()
        self.assertEqual(response.status_code, 200)

    def test_reject_with_reason(self):
        reason = "Test Reason"
        self.user = self.doctor
        url = reverse("update_request_status")
        response = self.client.post(
            url,
            {
                "recordID": self.health_record.id,
                "status": "rejected",
                "reason": reason,
            },
        )
        self.health_record.refresh_from_db()
        self.assertEqual(response.status_code, 200)


class viewAdminHealthHistoryTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_patient(
            email="user1@example.com",
            name="User1",
            password="userpass1",
            dob=datetime.strptime("1990-01-01", "%Y-%m-%d"),
            contactInfo="1234567890",
            proofOfIdentity="Proof1",
            address="Address1",
            securityQues="",
            securityAns="",
            bloodGroup="A+",
            is_staff=True,
        )
        self.appointment = Appointment.objects.create(
            name="Eye Test",
            properties=json.dumps(
                {
                    "cylindrical_power_right": 1.25,
                    "cylindrical_power_left": 0.75,
                    "spherical_power_left": -2.00,
                    "spherical_power_right": -1.50,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                }
            ),
        )
        self.health_record = HealthRecord.objects.create(
            doctorID=1,
            userID=self.user,
            hospitalID=1,
            status="approved",
            appointmentId=self.appointment,
        )
        self.hospital = Hospital.objects.create(
            name="Hospital A",
            address="Address A",
            contactInfo="1234567890",
        )
        self.hospital_staff = HospitalStaff.objects.create(
            hospitalID=self.hospital,
            admin=False,
            name="Doctor A",
            specialization="Cardiology",
            contactInfo="1234567890",
            userID=self.user.id,
        )

    def test_admin_view_history(self):
        url = reverse("admin_view_records")
        # appointment name healthcare_worker, healthcare_facility and date are passed
        request_struct = {
            "appointment_name": "Vaccine",
            "healthcare_worker": "Doctor A",
            "healthcare_facility": "Hospital A",
            "date": "2024-03-08",
        }
        request = self.factory.get(url, request_struct)
        request.user = self.user
        response = admin_view_health_history_requests(request)
        self.assertEqual(response.status_code, 200)

    def test_admin_view_history_requests(self):
        url = reverse("admin_view_records")
        # appointment name healthcare_worker, healthcare_facility date and record_status are passed
        request = HttpRequest()
        request.method = "GET"  # Set the HTTP method to GET
        request.path = url
        request.user = self.user
        request.GET["appointment_name"] = "Vaccine"
        request.GET["healthcare_worker"] = "Doctor A"
        request.GET["healthcare_facility"] = "Hospital B"
        request.GET["date"] = datetime.now().strftime(DATE_FORMAT)
        request.GET["record_status"] = "approved"
        response = admin_view_health_history_requests(request)
        self.assertEqual(response.status_code, 200)

    def test_admin_view_history_no_filters(self):
        url = reverse("admin_view_records")
        # appointment name healthcare_worker, healthcare_facility and date are passed
        request_struct = {}
        request = self.factory.get(url, request_struct)
        request.user = self.user
        response = admin_view_health_history_requests(request)
        self.assertEqual(response.status_code, 200)

    def test_admin_view_history_record_status(self):
        url = reverse("admin_view_records")
        # appointment name healthcare_worker, healthcare_facility and date are passed
        request_struct = {
            "appointment_name": "Vaccine",
            "healthcare_worker": "Doctor A",
            "healthcare_facility": "Hospital A",
            "date": "2024-03-08",
            "record_status": "pending",
        }
        request = self.factory.get(url, request_struct)
        request.user = self.user
        response = admin_view_health_history_requests(request)
        self.assertEqual(response.status_code, 200)

    def test_admin_edit_health_record_view(self):
        url = reverse("edit_record")
        body = {
            "recordId": "1",
            "appointmentId": "1",
            "appointmentType": "blood_test",
            "appointmentProperties": {"type": "Covid"},
            "doctorId": "1",
            "hospitalID": "1",
        }
        request = self.factory.post(
            url,
            data=body,
            content_type="application/json",
        )

        request.user = self.user
        response = get_admin_edit(request, 1)
        self.assertEqual(response.status_code, 200)


class HospitalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            email="testuser@test.com", password="12345"
        )
        self.client.login(email="testuser@test.com", password="12345")

        Hospital.objects.create(name="General Hospital", status="active")
        Hospital.objects.create(name="City Hospital", status="pending")
        Hospital.objects.create(name="Specialist Hospital", status="inactive")

    def test_list_hospitals_no_filter(self):
        response = self.client.get(reverse("list_hospitals"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("General Hospital", response.content.decode())

    def test_list_hospitals_with_filter(self):
        response = self.client.get(reverse("list_hospitals") + "?status=pending")
        self.assertEqual(response.status_code, 200)
        self.assertIn("City Hospital", response.content.decode())
        self.assertNotIn("General Hospital", response.content.decode())

    def test_update_hospital_status(self):
        hospital = Hospital.objects.get(name="General Hospital")
        response = self.client.post(
            reverse("update_hospital_status", args=[hospital.id]),
            data={"status": "inactive"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        hospital.refresh_from_db()
        self.assertEqual(hospital.status, "inactive")

    def test_update_hospital_status_invalid(self):
        hospital = Hospital.objects.get(name="General Hospital")
        response = self.client.post(
            reverse("update_hospital_status", args=[hospital.id]),
            data={"status": "unknown"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


class ViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_patient(
            email="patient@test.com", password="12345"
        )
        self.hospital = Hospital.objects.create(name="Test Hospital")
        self.client = Client()

    def test_get_patients(self):
        self.client.login(email="patient@test.com", password="12345")
        response = self.client.get(reverse("get_patients"))
        expected_patients = list(User.objects.filter(is_patient=True).values())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.json()["patients"]),
            len(expected_patients),
        )

    def test_get_doctor_details(self):
        self.client.login(email="patient@test.com", password="12345")
        doctor_user = User.objects.create_healthcare_worker(
            email="doctor@test.com", password="12345"
        )
        doctor = HospitalStaff.objects.create(
            id=1, userID=doctor_user.id, hospitalID=self.hospital
        )
        response = self.client.get(reverse("get_doctor_details", args=[doctor.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["user"],
            list(User.objects.filter(id=doctor.userID).values()),
        )

    def test_get_patient_details(self):
        self.client.login(email="patient@test.com", password="12345")
        patient = User.objects.create_patient(
            email="patient1@test.com", password="12345"
        )
        response = self.client.get(reverse("get_patient_details", args=[patient.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["user"], list(User.objects.filter(id=patient.id).values())
        )


class UserDashboardTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_patient(
            email="user1@example.com",
            password="userpass1",
            name="User1",
            dob="1990-01-01",
            contactInfo="1234567890",
            address="123 Main St",
            proofOfIdentity="SomeProof",
            bloodGroup="A+",
        )

        HealthHistoryAccessRequest.objects.create(
            requestorName="Test Requestor",
            requestorEmail="testrequestor@gmail.com",
            purpose="For onboarding process",
            userID=self.user,
        )

    def test_dashboard_view_access(self):
        url = reverse("user_dashboard")
        request = self.factory.get(url)
        request.user = self.user
        response = user_dashboard(
            request
        )  # Assuming user_dashboard is the correct view function
        self.assertEqual(response.status_code, 200)

    def test_user_not_patient(self):
        # Assuming a method or attribute that can change user role
        self.user.is_patient = False
        self.user.save()
        url = reverse("user_dashboard")
        request = self.factory.get(url)
        request.user = self.user
        response = user_dashboard(request)
        self.assertEqual(response.status_code, 302)


class viewDocHealthHistoryTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_patient(
            email="user1@example.com",
            name="User1",
            password="userpass1",
            dob=datetime.strptime("1990-01-01", "%Y-%m-%d"),
            contactInfo="1234567890",
            proofOfIdentity="Proof1",
            address="Address1",
            securityQues="",
            securityAns="",
            bloodGroup="A+",
            is_healthcare_worker=True,
        )
        self.appointment = Appointment.objects.create(
            name="Eye Test",
            properties=json.dumps(
                {
                    "cylindrical_power_right": 1.25,
                    "cylindrical_power_left": 0.75,
                    "spherical_power_left": -2.00,
                    "spherical_power_right": -1.50,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                }
            ),
        )
        self.health_record = HealthRecord.objects.create(
            doctorID=1,
            userID=self.user,
            hospitalID=1,
            status="pending",
            appointmentId=self.appointment,
        )
        self.hospital = Hospital.objects.create(
            name="Hospital A",
            address="Address A",
            contactInfo="1234567890",
        )
        self.hospital_staff = HospitalStaff.objects.create(
            hospitalID=self.hospital,
            admin=False,
            name="Doctor A",
            specialization="Cardiology",
            contactInfo="1234567890",
            userID=self.user.id,
        )

    def test_admin_view_history(self):
        url = reverse("admin_view_records")
        # appointment name healthcare_worker, healthcare_facility and date are passed
        request_struct = {
            "appointment_name": "Eye Test",
            "healthcare_worker": "Doctor A",
            "healthcare_facility": "Hospital A",
            "date": "2024-03-08",
        }
        request = self.factory.get(url, request_struct)
        request.user = self.user
        response = view_health_history_doc(request)
        self.assertEqual(response.status_code, 200)

    def test_admin_view_history_fail(self):
        url = reverse("admin_view_records")
        # appointment name healthcare_worker, healthcare_facility and date are passed
        request_struct = {
            "appointment_name": "Eye Test",
            "healthcare_worker": "Doctor A",
            "healthcare_facility": "Hospital A",
            "date": "2024-03-08",
        }
        request = self.factory.post(url, request_struct)
        request.user = self.user
        request.user.is_healthcare_worker = False
        # else case
        response = view_health_history_doc(request)
        self.assertEqual(response.status_code, 302)
