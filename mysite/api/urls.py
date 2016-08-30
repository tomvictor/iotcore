from django.conf.urls import url
from mysite.api.views import MsgListAPIView, MsgDetailView

urlpatterns = [
    url(r'^$', MsgListAPIView.as_view(), name='api'),
    url(r'^(?P<pk>\d+)/$', MsgDetailView.as_view(), name='detail')
]
