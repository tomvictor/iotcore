from django.db import models
from django.utils import timezone

# Create your models here.

class Mqtt(models.Model):
    msg = models.TextField()
    topic = models.CharField(max_length=180,default=" ")
    time = models.DateTimeField(auto_now=False,auto_now_add=True)

    def __str__(self):
        return self.msg

class Gps(models.Model):
    lat = models.CharField(max_length=500,blank=True)
    long = models.CharField(max_length=500,blank=True)
    speed = models.CharField(max_length=500,blank=True)
    time = models.DateTimeField(auto_now=False,auto_now_add=True)
    deviceId = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.deviceId
