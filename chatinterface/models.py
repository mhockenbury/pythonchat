from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    content = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField()
