from django.shortcuts import render,redirect
from .models import Mqtt
from django.utils import timezone
# Create your views here.

def home(request):
    return render(request,'home.html',{})


def store(request):
    message = request.GET.get("q")
    topic = request.GET.get("t")

    if message:
        print(str(message))
        m = Mqtt(msg=message)
        m.time = timezone.now()
        m.topic = topic
        m.save()
    return redirect("mysite:home")