import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_pin_value(value, pin_mode=None):
    if (
        not re.search(r'^(ON|OFF|\d{1,3})$', value) or
        re.search(r'^\d{1,3}$', value) and (int(value) < 0 or int(value) > 255)
    ):
        raise ValidationError(
            message=_('The value must "ON", "OFF" or an integer from 0 to 255'),
            code='invalid',
        )

def validate_digital_pin(value):
    if not re.search(r'^(ON|OFF)$', value):
        raise ValidationError(
            message=_('The digital pin value must "ON" or "OFF"'),
            code='invalid',
        )
