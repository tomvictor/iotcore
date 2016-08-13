from django.shortcuts import render,redirect
from .models import Mqtt
from django.utils import timezone
# Create your views here.

def home(request):
    return render(request,'home.html',{})


def store(request):
    query = request.GET.get("q")
    if query:
        print(str(query))
        m = Mqtt(msg=query)
        m.time = timezone.now()
        m.topic = "none"
        m.save()
    return redirect("mysite:home")