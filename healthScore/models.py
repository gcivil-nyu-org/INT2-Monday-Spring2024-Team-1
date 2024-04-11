from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    PermissionsMixin,
    AbstractBaseUser,
)


STATUS_CHOICES = [
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("pending", "Pending"),
]


# Create your models here.
class Hospital(models.Model):  # Viewed by healthScoreAdmin and hospitalAdmin
    id = models.AutoField(primary_key=True)
    name = models.TextField(null=False)
    address = models.TextField(null=False)
    contactInfo = models.TextField(null=False, max_length=10)
    status = models.TextField(choices=STATUS_CHOICES, default="pending")


class HospitalStaff(models.Model):  # Viewed by hospitalAdmin
    id = models.AutoField(primary_key=True)
    hospitalID = models.ForeignKey("hospital", to_field="id", on_delete=models.CASCADE)
    admin = models.BooleanField(default=False)  # True = hospitalAdmin, False = Doctor
    name = models.TextField(null=False)
    specialization = models.TextField(default="")
    contactInfo = models.TextField(default="", max_length=10)
    userID = models.IntegerField(null=False)
    securityQues = models.TextField(
        default=""
    )  # If we not doing email resetting password
    securityAns = models.TextField(
        default=""
    )  # If we not doing email resetting password


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("You have not provided a valid email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_patient(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_patient", True)
        return self._create_user(email, password, **extra_fields)

    def create_staff(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_patient", False)
        return self._create_user(email, password, **extra_fields)

    def create_healthcare_worker(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_patient", False)
        extra_fields.setdefault("is_healthcare_worker", True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_healthcare_worker", False)
        extra_fields.setdefault("is_patient", False)
        extra_fields.setdefault("is_superuser", True)

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):  # Viewed by User
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.TextField(null=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)
    is_healthcare_worker = models.BooleanField(default=False)

    last_login = models.DateTimeField(blank=True, null=True)

    name = models.TextField(blank=True, max_length=255, default="")
    dob = models.DateField(blank=True, null=True)
    contactInfo = models.TextField(default="", max_length=10)
    address = models.TextField(null=False)
    proofOfIdentity = models.TextField(
        null=False
    )  # Convert image to base64 string and store it here

    securityQues = models.TextField(
        default=""
    )  # If we not doing email resetting password
    securityAns = models.TextField(
        default=""
    )  # If we not doing email resetting password
    gender = models.TextField(
        blank=True, default=""
    )  # Can be updated to a choice field later on, if needed
    profilePic = models.TextField(
        null=True
    )  # Convert image to base64 string and store it here
    bloodGroup = models.TextField(null=False)
    requests = models.JSONField(
        null=True
    )  # Will store data in this form: [{ requestedBy: '', dateTime:'', status:''}]. Will have
    # the data of all the requests that have been done to view the user's records

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def get_full_name(self):
        return self.name


class HealthRecord(models.Model):  # Viewed by User and hospitalStaff who are doctors
    id = models.AutoField(primary_key=True)
    doctorID = models.IntegerField(null=False)
    userID = models.ForeignKey("user", to_field="id", on_delete=models.CASCADE)
    hospitalID = models.IntegerField(null=False)
    status = models.TextField(choices=STATUS_CHOICES, default="pending")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now_add=True)
    appointmentId = models.ForeignKey(
        "appointment", to_field="id", on_delete=models.CASCADE
    )
    healthDocuments = models.JSONField(null=True)
    rejectedReason = models.TextField(null=True)


class Appointment(models.Model):  # Viewed by User and hospitalStaff who are doctors
    id = models.AutoField(primary_key=True)
    name = models.TextField(null=False)
    properties = models.JSONField(null=True)
    # Will store values such as below. Need not be only vaccines
    # {     # Can be a null field
    #     name  -> vaccine
    #     value -> covid
    # }


class CommunityInteraction(models.Model):
    userID = models.ForeignKey("user", to_field="id", on_delete=models.CASCADE)
    postID = models.AutoField(primary_key=True)
    postTitle = models.TextField(null=False)
    postDescription = models.TextField(default="")
    postTimeStamp = models.DateTimeField(auto_now_add=True)
    upvote = models.IntegerField(default=0)
    downvote = models.IntegerField(default=0)
    tags = models.TextField(default="")
    postComments = models.JSONField(null=True)
    # These are the values that would be stored in the postComments jsonField
    # [{
    #     comment
    #     commentID
    #     commentTimeStamp
    #     commentUpvotes
    #     commentDownvotes
    #     userIdOfCommenter
    # }]


class Post(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    title = models.TextField(null=False)
    description = models.TextField(default="")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    post = models.ForeignKey("Post", related_name="comments", on_delete=models.CASCADE)
    commenter = models.ForeignKey("User", on_delete=models.CASCADE)
    content = models.TextField(default="")
    createdAt = models.DateTimeField(auto_now_add=True)


# 3rd Party requests
class HealthHistoryAccessRequest(models.Model):
    id = models.AutoField(primary_key=True)
    userID = models.ForeignKey("user", to_field="id", on_delete=models.CASCADE)
    status = models.TextField(choices=STATUS_CHOICES, default="pending")
    requestorName = models.TextField(null=False)
    requestorEmail = models.EmailField(null=False)
    purpose = models.TextField(null=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now_add=True)
