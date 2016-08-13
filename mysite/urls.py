from django.conf.urls import url
from mysite import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^store/$', views.store, name='store'),
]
