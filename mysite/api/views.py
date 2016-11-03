
from mysite.models import Mqtt
from mysite.api.serializers import MsgListSerializer,MsgDetailSerializer,MsgCreateSerializer
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView
    )

class MsgCreateAPIView(CreateAPIView):
    queryset = Mqtt.objects.all()
    serializer_class = MsgCreateSerializer


class MsgListAPIView(ListAPIView):
    queryset = Mqtt.objects.all()
    serializer_class = MsgListSerializer


class MsgDetailView(RetrieveAPIView):
    queryset = Mqtt.objects.all()
    serializer_class = MsgDetailSerializer

class MsgUpdateView(UpdateAPIView):
    queryset = Mqtt.objects.all()
    serializer_class = MsgDetailSerializer


class MsgDeleteView(DestroyAPIView):
    queryset = Mqtt.objects.all()
    serializer_class = MsgDetailSerializer
