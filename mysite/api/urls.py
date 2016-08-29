from django.conf.urls import url, include
from mysite import views
from mysite.api.views import MsgListAPIView

urlpatterns = [
    url(r'^$', MsgListAPIView.as_view(), name='api'),
]
