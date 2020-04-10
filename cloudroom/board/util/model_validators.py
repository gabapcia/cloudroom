def pin_validator(status, configuration, from_rest=False):
    if from_rest:
        from rest_framework.serializers import ValidationError
    else:
        from django.core.exceptions import ValidationError

    if configuration == 0:
        if status not in ('ON', 'OFF'):
            raise ValidationError(
                f'{status} is not a valid status for a digital pin'
            )
    else:
        MAX_VALUE = 1023
        MIN_VALUE = 0
        try:
            value_parsed = int(status)
            if value_parsed > MAX_VALUE or value_parsed < MIN_VALUE:
                raise ValidationError(
                    f'{status} is out of range. Shoud be from 0 to 1023'
                )

        except ValueError:
            raise ValidationError(
                f'{status} is not a valid status. Shoud be an Integer from 0 to 1023'
            )
