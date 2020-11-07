import re
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


def validate_pin_value(value):
    if re.search(r'^\d{1,4}$', value):
        value = int(value)
        if value > 1023 or value < 0:
            raise ValidationError(_('Pin value must be between 0 and 1023'))
    elif not re.search(r'^ON|OFF$', value):
        raise ValidationError(_('Pin value must be ON or OFF'))
