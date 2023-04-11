from django.db import models
from django.contrib.auth.models import User
import uuid, json
# Create your models here.



class Profile(models.Model):
    p_id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    user = models.OneToOneField(User, related_name='userprofile', on_delete=models.CASCADE)
    room_id = models.CharField(max_length=8, unique=True)
    created_at = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.user

class Message(models.Model):
    user = models.ForeignKey(Profile, related_name="chat_user", on_delete=models.CASCADE)
    text = models.TextField()
    media = models.URLField(blank=True, null=True)
    sent_by = models.CharField(max_length=8)
    sent_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.user

class ChatHistory(models.Model):
    user_id = models.CharField(max_length=16)
    question = models.TextField(null=True, blank=True)
    chat_history = models.TextField(null=True, blank=True)