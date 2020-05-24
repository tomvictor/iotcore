from django.urls import path

from djangoiot import views

app_name = "djangoiot"

urlpatterns = [
    path("brokers/", views.Brokers.as_view(), name="brokers"),
]
