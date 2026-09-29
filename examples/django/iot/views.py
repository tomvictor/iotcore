from django.http import JsonResponse

from iotcore import IotCore

# Django's runserver autoreloader runs this module twice; the second IotCore sees the
# port is taken and only connects a client instead of starting another broker.
iot = IotCore()
iot.start()
latest = {}


@iot.accept("sensors/#")
def on_sensor(topic, data):
    latest[topic] = data


def home(request):
    return JsonResponse({"latest": latest})


def publish(request):
    topic = request.GET.get("topic", "sensors/temperature")
    iot.publish(topic, request.GET.get("data", "21.5"))
    return JsonResponse({"published": topic})


def unsubscribe(request):
    iot.unsubscribe("sensors/#")
    return JsonResponse({"unsubscribed": "sensors/#"})
