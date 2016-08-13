from django.shortcuts import render,redirect
from .models import Mqtt
# Create your views here.

def home(request):
    return render(request,'home.html',{})


def store(request):
    query = request.GET.get("q")
    if query:
        print(str(query))
        m = Mqtt()
    return redirect("mysite:home")