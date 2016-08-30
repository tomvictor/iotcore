from django.db import models
from django.utils import timezone

# Create your models here.

class Mqtt(models.Model):
    msg = models.TextField()
    topic = models.CharField(max_length=180,default=" ")
    time = models.DateTimeField(auto_now=False,auto_now_add=True)

    def __str__(self):
        return self.msg