from django.http import JsonResponse
from iotcore import IotCore

iot = IotCore()
iot.background_loop_forever()


def mqtt_callback(data):
    print(f"Django >: {data}")


def subscribe(request):
    iot.subscribe("iot", mqtt_callback)
    return JsonResponse({"response": "subscribed"})


def publish(request):
    iot.publish("iot", "demo")
    return JsonResponse({"response": "published"})
