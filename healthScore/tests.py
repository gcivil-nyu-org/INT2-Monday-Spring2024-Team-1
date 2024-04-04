from django.test import RequestFactory, TransactionTestCase, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import HttpRequest
import os
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

from healthScore.views import (
    edit_user_info,
    view_health_history,
    view_report,
    view_user_info,
    view_health_history_requests,
    add_health_record_view,
    record_sent_view,
    activate_healthcare_staff,
    deactivate_healthcare_staff,
    create_post,
    view_all_posts,
    view_post,
    create_comments,
    get_doctors,
    get_record,
    get_edit,
    edit_health_record_view,
    add_healthcare_staff,
    request_health_history,
    view_health_history_access_requests,
    update_health_history_access_request_status,
    delete_post,
    edit_post,
    delete_comment,
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
            dob="1990-01-01",
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
        response = edit_health_record_view(request)
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
        self.factory = RequestFactory()
        self.user = User.objects.create(
            email="admin@example.com", password="testpass123", is_patient=1, is_active=1
        )
        HealthHistoryAccessRequest.objects.create(
            id=1,
            status="pending",
            requestorName="NYU",
            requestorEmail="shc@nyu.edu",
            purpose="For medical clearances",
            userID=self.user,
        )
        HealthHistoryAccessRequest.objects.create(
            id=2,
            status="pending",
            requestorName="NYU",
            requestorEmail="",
            purpose="For medical clearances",
            userID=self.user,
        )

    def test_approve_request(self):
        request = self.factory.put(
            reverse("update_health_history_access_request_status"),
            data={"request_id": 1, "status": "approved"},
            content_type="application/json",
        )

        request.user = self.user
        response = update_health_history_access_request_status(request)
        self.assertEqual(response.status_code, 200)

    def test_reject_request(self):
        request = self.factory.put(
            reverse("update_health_history_access_request_status"),
            data={"request_id": 1, "status": "rejected"},
            content_type="application/json",
        )

        request.user = self.user
        response = update_health_history_access_request_status(request)
        self.assertEqual(response.status_code, 200)

    def test_email_sent(self):
        request = self.factory.put(
            reverse("update_health_history_access_request_status"),
            data={"request_id": 1, "status": "approved"},
            content_type="application/json",
        )

        request.user = self.user
        response = update_health_history_access_request_status(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Email sent and request status updated successfully",
            response.content.decode(),
        )

    def test_email_not_sent(self):
        request = self.factory.put(
            reverse("update_health_history_access_request_status"),
            data={"request_id": 2, "status": "rejected"},
            content_type="application/json",
        )

        request.user = self.user
        response = update_health_history_access_request_status(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Email could not be sent, but request status updated successfully",
            response.content.decode(),
        )

    def test_unauthorized_error(self):
        request = self.factory.post(
            reverse("update_health_history_access_request_status"),
            data={"request_id": 1, "status": "approved"},
            content_type="application/json",
        )

        request.user = self.user
        response = update_health_history_access_request_status(request)
        self.assertEqual(response.status_code, 401)


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
