from rest_framework.serializers import ModelSerializer,HyperlinkedIdentityField
from mysite.models import Mqtt,Gps

class MsgListSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(
        view_name='restapi:api-detail'
    )
    class Meta:
        model = Gps
        fields = [
            'url',
            'id',
            'lat',
            'lng',
            'speed',
            'deviceId',
            'time'
        ]

class MapSerializer(ModelSerializer):
    class Meta:
        model = Gps
        fields = [
            'lat',
            'lng',
        ]

class MsgCreateSerializer(ModelSerializer):
    class Meta:
        model = Gps
        fields = [
            'lat',
            'lng',
            'speed',
            'deviceId',
        ]


class MsgDetailSerializer(ModelSerializer):
    class Meta:
        model = Gps
        fields = [
            'id',
            'lat',
            'lng',
            'speed',
            'deviceId',
            'time'
        ]



"""
data = {
    "msg" : "Tom testing rest",
    "topic" : "hai",
    "time" : "2016-08-13 12:36:47.711279"
}

new_data = MsgListSerializer(data=data)
if new_data.is_valid():
    new_data.save()
else:
    print(new_data.errors)

"""
