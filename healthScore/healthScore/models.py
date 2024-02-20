import datetime
from django.db import models
from django.utils import timezone


STATUS_CHOICES = [
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("pending", "Pending")
]

# Create your models here.
class hospitals(models.Model):    # Viewed by healthScoreAdmin and hospitalAdmin
    id = models.AutoField(primary_key=True)
    name = models.TextField(Null=False)
    address = models.TextField(Null=False)
    email = models.EmailField(Null=False)    # Super admin's account
    password = models.TextField(Null=False) # Super admin's account    # Needs to be updated once password is hashed
    contactInfo = models.IntegerField(Null=False, default="", max_length=10)
    website = models.TextField(Null=False, default="")
    status = models.TextField(choices=STATUS_CHOICES, default="rejected")


class hospitalStaff(models.Model):   # Viewed by hospitalAdmin
    id = models.AutoField(primary_key=True)
    hospitalID = models.ForeignKey("hospitals", to_field="id", on_delete=models.CASCADE)
    admin = models.BooleanField(default=False, Null=True)   # True = hospitalAdmin, False = Doctor
    name = models.TextField(Null=False)
    email = models.EmailField(Null=False)
    password = models.TextField(Null=False) # Needs to be updated once password is hashed
    specialization = models.TextField(Null=False, default="")
    contactInfo = models.IntegerField(Null=False, default="", max_length=10)
    securityQues = models.TextField(Null=False, default="") # If we not doing email resetting password
    securityAns = models.TextField(Null=False, default="") # If we not doing email resetting password


class user(models.Model): # Viewed by User
    id = models.AutoField(primary_key=True)
    email = models.EmailField(Null=False)
    name = models.TextField(Null=False)
    password = models.TextField(Null=False)
    userName = models.TextField(Null=False, unique=True)
    dob = models.DateField(Null=False)
    contactInfo = models.IntegerField(Null=False, default="", max_length=10)
    proofOfIdentity = models.TextField(Null=True)    # Convert image to base64 string and store it here
    address = models.TextField(Null=False)
    securityQues = models.TextField(Null=False, default="")   # If we not doing email resetting password
    securityAns = models.TextField(Null=False, default="")   # If we not doing email resetting password
    gender = models.TextField(Null=False, default="")  # Can be updated to a choice field later on, if needed 
    profilePic = models.TextField(Null=True)    # Convert image to base64 string and store it here
    bloodGroup = models.TextField(Null=False)
    requests = models.JSONField(Null=True) # Will store data in this form: [{ requestedBy: '', dateTime:'', status:''}]. Will have 
                                # the data of all the requests that have been done to view the user's records


class healthRecord(models.Model): # Viewed by User and hospitalStaff who are doctors
    id = models.AutoField(primary_key=True)
    doctorID = models.ForeignKey("hospitalStaff", to_field="id")                  
    userID = models.ForeignKey("user", to_field="id")                                                           
    hospitalID = models.ForeignKey("hospitals", to_field="id")                                                       
    status = models.TextField(choices=STATUS_CHOICES, default="rejected")
    dateTime = models.DateTimeField(Null=False, default=datetime.date.today())                                       
    appointmentId = models.ForeignKey("appointment", to_field="id")                                                                                       
    healthDocuments = models.ArrayField(Null=True)

class appointment(models.Model): # Viewed by User and hospitalStaff who are doctors
    id = models.AutoField(primary_key=True)
    appointmentName = models.TextField(Null=False)
    appointmentProperties = models.JSONField(Null=True)
    # Will store values such as below. Need not be only vaccines
    # {     # Can be a null field
    #     name  -> vaccine
    #     value -> covid
    # }


class communityInteraction:
    userID = models.ForeignKey("user", to_field="id")                                                           
    userName = models.ForeignKey("user", to_field="userName")   # Not really sure as to how this value would be set in the model
    postID = models.AutoField(primary_key=True)
    postTitle = models.TextField(Null=False, default="")
    postDescription = models.TextField(Null=False, default="")
    postTimeStamp = models.DateTimeField(Null=False, default=datetime.date.today())                                       
    upvote = models.IntegerField(Null=False, default=0)
    downvote = models.IntegerField(Null=False, default=0)
    tags = models.TextField(Null=True, default="")
    postComments = models.JSONField(Null=True)
    # These are the values that would be stored in the postComments jsonField
    # [{
    #     comment
    #     commentID
    #     commentTimeStamp
    #     commentUpvotes
    #     commentDownvotes
    #     userIdOfCommenter
    # }]