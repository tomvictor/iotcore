from django.db import models

# Create your models here.

class Mqtt(models.Model):
    msg = models.TextField()
    topic = models.CharField(max_length=180,default=" ")
    time = models.DateTimeField(blank=True)

    def __str__(self):
        return self.msg