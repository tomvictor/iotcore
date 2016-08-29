from rest_framework.serializers import ModelSerializer
from mysite.models import Mqtt

class MsgSerializer(ModelSerializer):
    class Meta:
        model = Mqtt
        fields = [
            'id',
            'msg',
            'topic',
        ]