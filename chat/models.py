from django.db import models
from healthScore.models import User


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=False)
    createdAt = models.DateTimeField(auto_now_add=True)


class ChatSession(models.Model):
    patient = models.ForeignKey(
        User, related_name="patient_chats", on_delete=models.CASCADE
    )
    healthcareWorker = models.ForeignKey(
        User, related_name="worker_chats", on_delete=models.CASCADE
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    messages = models.ManyToManyField(Message, blank=True)
