from django.test import RequestFactory, TransactionTestCase, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import HttpRequest

from datetime import datetime
import json

from healthScore.models import (
    HealthRecord,
    Hospital,
    User,
    HospitalStaff,
    Appointment,
    Post,
)

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
    view_posts,
    view_one_topic,
    create_comments,
    get_doctors,
    get_record,
    get_edit,
    edit_health_record_view,
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
        self.assertEqual(response.status_code, 400)

    def test_deactivate_healthcare_staff_pass(self):
        request = self.factory.put(
            reverse("deactivate_healthcare_staff"),
            data={"user_id": 2},
            content_type="application/json",
        )

        request.user = self.user
        response = deactivate_healthcare_staff(request)
        self.assertEqual(response.status_code, 200)

class PostCommentTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user1 = User.objects.create(
            id=5,
            email="patient@example.com",
            name="User 1",
            password="patientpass",
        )
        self.post = Post.objects.create(
            title="Test Post", description="Test Description", user=self.user1
        )

    def test_view_posts(self):
        request = self.factory.get("/viewPosts")
        response = view_posts(request)
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        request = self.factory.post(
            "/createPost", {"title": "Test Title", "description": "Test Description"}
        )
        request.user = self.user1
        response = create_post(request)
        self.assertEqual(response.status_code, 302)

    def test_view_one_topic(self):
        request = self.factory.get(f"/view_one_topic/{self.post.id}/")
        response = view_one_topic(request, post_id=self.post.id)
        self.assertEqual(response.status_code, 200)

    def test_create_comments(self):
        comment_data = {"content": "Test Comment"}
        request = self.factory.post(
            f"/create_comments/{self.post.id}/comment/", comment_data
        )
        request.user = self.user1
        response = create_comments(request, post_id=self.post.id)
        self.assertEqual(response.status_code, 302)
