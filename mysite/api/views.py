
from mysite.models import Mqtt,Gps
from mysite.api.serializers import MsgListSerializer,MsgDetailSerializer,MsgCreateSerializer,MapSerializer
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView
    )

class MsgCreateAPIView(CreateAPIView):
    queryset = Gps.objects.all()
    serializer_class = MsgCreateSerializer


class MsgListAPIView(ListAPIView):
    queryset = Gps.objects.all()
    serializer_class = MsgListSerializer


class MsgDetailView(RetrieveAPIView):
    queryset = Gps.objects.all()
    serializer_class = MsgDetailSerializer

class MsgUpdateView(UpdateAPIView):
    queryset = Gps.objects.all()
    serializer_class = MsgDetailSerializer


class MsgDeleteView(DestroyAPIView):
    queryset = Gps.objects.all()
    serializer_class = MsgDetailSerializer


#Googe map

class GoogleMapAPIView(ListAPIView):
    queryset = Gps.objects.all()
    serializer_class = MapSerializer