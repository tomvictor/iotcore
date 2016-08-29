from rest_framework.generics import ListAPIView
from mysite.models import Mqtt
from mysite.api.serializers import MsgSerializer


class MsgListAPIView(ListAPIView):
    queryset = Mqtt.objects.all()
    serializer_class = MsgSerializer