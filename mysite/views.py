from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Mqtt,Gps
from django.utils import timezone
# Create your views here.


def home(request):
    all_entries = Gps.objects.order_by("-time")
    latest = Gps.objects.last()
    # print(latest.lat)

    context_pass = {
        "objects":all_entries,
        "lat":latest.lat,
        "long":latest.long,
    }
    return render(request,'home.html',context_pass)

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


def log_data(request):
    if request.method == 'GET':
        lat_info = request.GET.get("lat")
        long_info = request.GET.get("long")
        device_info = request.GET.get("device_id")
        this_object = Gps(lat=lat_info,long=long_info,deviceId=device_info)
        this_object.save()
        print(lat_info)
        return HttpResponse("Ok, Data Stored")
    else:
        return redirect("mysite:home")
