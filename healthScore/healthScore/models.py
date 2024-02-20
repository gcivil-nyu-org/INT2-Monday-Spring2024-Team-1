import datetime
from django.db import models
from django.utils import timezone


STATUS_CHOICES = [
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("pending", "Pending")
]

# Create your models here.
class hospital(models.Model):    # Viewed by healthScoreAdmin and hospitalAdmin
    id = models.AutoField(primary_key=True)
    name = models.TextField(null=False, default="")
    address = models.TextField(null=False, default="")
    email = models.EmailField(null=False)    # Super admin's account
    password = models.TextField() # Super admin's account    
    contactInfo = models.TextField(null=False, default="", max_length=10)
    website = models.TextField(null=False, default="")
    status = models.TextField(choices=STATUS_CHOICES, default="pending")


class hospitalStaff(models.Model):   # Viewed by hospitalAdmin
    id = models.AutoField(primary_key=True)
    hospitalID = models.ForeignKey("hospital", to_field="id", on_delete=models.CASCADE)
    admin = models.BooleanField(default=False, null=True)   # True = hospitalAdmin, False = Doctor
    name = models.TextField(null=False)
    email = models.EmailField(null=False)
    password = models.TextField(null=False) 
    specialization = models.TextField(null=False, default="")
    contactInfo = models.TextField(null=False, default="", max_length=10)
    securityQues = models.TextField(null=False, default="") # If we not doing email resetting password
    securityAns = models.TextField(null=False, default="") # If we not doing email resetting password


class user(models.Model): # Viewed by User
    id = models.AutoField(primary_key=True)
    email = models.EmailField(null=False)
    name = models.TextField(null=False)
    password = models.TextField(null=False)
    userName = models.TextField(null=False, unique=True)
    dob = models.DateField(null=False)
    contactInfo = models.TextField(null=False, default="", max_length=10)
    proofOfIdentity = models.TextField(null=True)    # Convert image to base64 string and store it here
    address = models.TextField(null=False)
    securityQues = models.TextField(null=False, default="")   # If we not doing email resetting password
    securityAns = models.TextField(null=False, default="")   # If we not doing email resetting password
    gender = models.TextField(null=False, default="")  # Can be updated to a choice field later on, if needed 
    profilePic = models.TextField(null=True)    # Convert image to base64 string and store it here
    bloodGroup = models.TextField(null=False)
    requests = models.JSONField(null=True) # Will store data in this form: [{ requestedBy: '', dateTime:'', status:''}]. Will have 
                                # the data of all the requests that have been done to view the user's records


class healthRecord(models.Model): # Viewed by User and hospitalStaff who are doctors
    id = models.AutoField(primary_key=True)
    doctorID = models.TextField(default="", null=False)                                                       
    userID = models.ForeignKey("user", to_field="id", on_delete=models.CASCADE)                                                           
    hospitalID = models.TextField(default="", null=False)                                                       
    status = models.TextField(choices=STATUS_CHOICES, default="pending")
    createdAt = models.DateTimeField(null=False, default=datetime.datetime.now())                                       
    updatedAt = models.DateTimeField(null=False, default=datetime.datetime.now())                                       
    appointmentId = models.ForeignKey("appointment", to_field="id", on_delete=models.CASCADE)                                                                                       
    healthDocuments = models.JSONField(null=True)

class appointment(models.Model): # Viewed by User and hospitalStaff who are doctors
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
    postTitle = models.TextField(null=False, default="")
    postDescription = models.TextField(null=False, default="")
    postTimeStamp = models.DateTimeField(null=False, default=datetime.datetime.now())                                       
    upvote = models.IntegerField(null=False, default=0)
    downvote = models.IntegerField(null=False, default=0)
    tags = models.TextField(null=True, default="")
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