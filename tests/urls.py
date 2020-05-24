from django.urls import include, path

from tests import views

app_name = "test_app"
urlpatterns = [
    path("", include("djangoiot.urls", namespace="djangoiot")),
    path("test/", views.TestView.as_view(), name="test-view"),
]
