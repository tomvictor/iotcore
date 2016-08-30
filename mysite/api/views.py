from rest_framework.generics import ListAPIView,RetrieveAPIView
from mysite.models import Mqtt
from mysite.api.serializers import MsgListSerializer


class MsgListAPIView(ListAPIView):
    queryset = Mqtt.objects.all()
    serializer_class = MsgListSerializer


class MsgDetailView(RetrieveAPIView):
    queryset = Mqtt.objects.all()
    serializer_class = MsgListSerializer