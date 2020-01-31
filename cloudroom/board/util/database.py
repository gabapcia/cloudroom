from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Validator:
    @staticmethod
    def status_validation(value: int, type_: str):
        if type_ == 0:
            if value not in ('ON', 'OFF'):
                raise ValidationError(
                    _('%(value)s is not a valid status for a digital pin'),
                    params={'value': value},
                )
        else:
            MAX_VALUE = 1023
            MIN_VALUE = 0
            try:
                value_parsed = int(value)
                if value_parsed > MAX_VALUE or value_parsed < MIN_VALUE:
                    raise ValidationError(
                        _('%(value)s is out of range. Shoud be from 0 to 1023'),
                        params={'value': value},
                    )
            except ValueError:
                raise ValidationError(
                    _('%(value)s is not a valid status. Shoud be an Integer from 0 to 1023'),
                    params={'value': value},
                )