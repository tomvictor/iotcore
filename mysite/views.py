from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Mqtt
from django.utils import timezone
# Create your views here.

def home(request):
    allmessages = Mqtt.objects.order_by("-time")
    return render(request,'home.html',{"objects":allmessages})


def store(request):
    message = request.GET.get("q")
    topic = request.GET.get("t")

    if message:
        print(str(message))
        m = Mqtt(msg=message)
        m.time = timezone.now()
        m.topic = topic
        m.save()
        return HttpResponse("OK,data stored in database")
    else:
        return redirect("mysite:home")