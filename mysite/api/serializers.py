from rest_framework.serializers import ModelSerializer
from mysite.models import Mqtt

class MsgListSerializer(ModelSerializer):
    class Meta:
        model = Mqtt
        fields = [
            'id',
            'msg',
        ]

class MsgDetailSerializer(ModelSerializer):
    class Meta:
        model = Mqtt
        fields = [
            'id',
            'msg',
            'topic',
            'time',
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
