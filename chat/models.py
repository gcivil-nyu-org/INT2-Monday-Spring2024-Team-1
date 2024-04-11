from django.db import models
from healthScore.models import User


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=False)
    createdAt = models.DateTimeField(auto_now_add=True)