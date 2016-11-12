from django.conf.urls import url, include
from mysite import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^store/$', views.store, name='store'),
    url(r'^log/$', views.log_data, name='log_data'),
    url(r'^latest/$', views.latest_entry, name='latest'),
]
