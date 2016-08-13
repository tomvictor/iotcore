from django.shortcuts import render,redirect

# Create your views here.

def home(request):
    return render(request,'home.html',{})


def store(request):
    query = request.GET.get("q")
    if query:
        print(str(query))
    return redirect("mysite:home")