from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Mqtt,Gps
from django.utils import timezone
import requests
# Create your views here.


def home(request):
    all_entries = Gps.objects.order_by("-time")
    table_entries = Gps.objects.order_by("-time")
    latest = Gps.objects.last()
    # print(latest.lat)
    url = "http://iot.buildfromzero.com/api/map/?format=json"
    r = requests.get(url)
    draw = r.json()
    print(r.json())
    context_pass = {
        "objects":table_entries,
        "lat":latest.lat,
        "lng":latest.lng,
        "drawable":draw,
        "mapobjects":all_entries
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
        lng_info = request.GET.get("lng")
        device_info = request.GET.get("device_id")
        this_object = Gps(lat=lat_info,lng=lng_info,deviceId=device_info)
        this_object.save()
        print(lat_info)
        return HttpResponse("Ok, Data Stored")
    else:
        return redirect("mysite:home")


def latest_entry(request):
    queryset = Gps.objects.last()
    object_pk = queryset.pk
    #print(object_pk)
    url = str(object_pk)
    url = "/api/"+ url + "/" + "?format=json"
    print(url)
    return redirect(url)
