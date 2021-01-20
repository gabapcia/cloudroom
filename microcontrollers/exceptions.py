from rest_framework.exceptions import APIException


class HashSecretError(Exception):
    pass


class BrokerConnectionError(APIException):
    status_code = 503
    default_detail = \
        'MQTT Broker service temporarily unavailable, try again later'
    default_code = 'mqtt_broker_service_unavailable'
