from rest_framework.generics import ListAPIView
from mysite.models import Mqtt

class MsgListAPIView(ListAPIView):
    queryset = Mqtt.objects.all()