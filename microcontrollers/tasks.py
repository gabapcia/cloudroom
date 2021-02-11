from celery import shared_task
from cloudroom.mqtt.rabbitmq import Manager as MQTTManager
from cloudroom.mqtt.exceptions import BrokerPublishError
from .models import Pin
from .serializers.pin import BasicPinInfoSerializer


@shared_task(
    autoretry_for=[BrokerPublishError],
    max_retries=5,
)
def notify_board(topic: str, pin_id: int) -> None:
    pin = Pin.objects.get(pk=pin_id)
    payload = BasicPinInfoSerializer(pin).data
    manager = MQTTManager()
    manager.publish(topic=topic, payload=payload)


@shared_task
def change_pin_value(pin_id: int, value: str) -> None:
    pin = Pin.objects.get(pk=pin_id)
    pin.value = value
    pin.save()
