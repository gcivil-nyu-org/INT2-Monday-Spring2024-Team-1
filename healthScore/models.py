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
class hospital(models.Model):  # Viewed by healthScoreAdmin and hospitalAdmin
    id = models.AutoField(primary_key=True)
    name = models.TextField(null=False)
    address = models.TextField(null=False)
    email = models.EmailField(null=False)  # Super admin's account
    password = models.TextField()  # Super admin's account
    contactInfo = models.TextField(null=False, max_length=10)
    website = models.TextField(default="")
    status = models.TextField(choices=STATUS_CHOICES, default="pending")


class hospitalStaff(models.Model):  # Viewed by hospitalAdmin
    id = models.AutoField(primary_key=True)
    hospitalID = models.ForeignKey("hospital", to_field="id", on_delete=models.CASCADE)
    admin = models.BooleanField(default=False)  # True = hospitalAdmin, False = Doctor
    name = models.TextField(null=False)
    email = models.EmailField(null=False)
    password = models.TextField(null=False)
    specialization = models.TextField(default="")
    contactInfo = models.TextField(default="", max_length=10)
    securityQues = models.TextField(
        default=""
    )  # If we not doing email resetting password
    securityAns = models.TextField(
        default=""
    )  # If we not doing email resetting password


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            email=self.normalize_email(email), username=username, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        return self.create_user(email, username, password, **extra_fields)


class user(AbstractBaseUser, PermissionsMixin):  # Viewed by User
    id = models.AutoField(primary_key=True)
    email = models.EmailField(null=False)
    name = models.TextField(null=False)
    password = models.TextField(null=False)
    username = models.CharField(null=False, max_length=50, unique=True)
    dob = models.DateField(null=False)
    contactInfo = models.TextField(default="", max_length=10)
    proofOfIdentity = models.TextField(
        null=False
    )  # Convert image to base64 string and store it here
    address = models.TextField(null=False)
    securityQues = models.TextField(
        default=""
    )  # If we not doing email resetting password
    securityAns = models.TextField(
        default=""
    )  # If we not doing email resetting password
    gender = models.TextField(
        default=""
    )  # Can be updated to a choice field later on, if needed
    profilePic = models.TextField(
        null=True
    )  # Convert image to base64 string and store it here
    bloodGroup = models.TextField(null=False)
    requests = models.JSONField(
        null=True
    )  # Will store data in this form: [{ requestedBy: '', dateTime:'', status:''}]. Will have
    # the data of all the requests that have been done to view the user's records

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = CustomUserManager()


class healthRecord(models.Model):  # Viewed by User and hospitalStaff who are doctors
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


class appointment(models.Model):  # Viewed by User and hospitalStaff who are doctors
    id = models.AutoField(primary_key=True)
    name = models.TextField(null=False)
    properties = models.JSONField(null=True)
    # Will store values such as below. Need not be only vaccines
    # {     # Can be a null field
    #     name  -> vaccine
    #     value -> covid
    # }


class communityInteraction(models.Model):
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
