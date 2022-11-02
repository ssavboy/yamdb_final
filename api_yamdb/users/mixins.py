import re

from django.core.exceptions import ValidationError


class UsernameValidatorMixin:
    regex = re.compile(r'^[\w.@+-]+$')

    def validate_username(self, value):
        if value.lower() == 'me':
            raise ValidationError(message='Username "me" не валиден.')
        if not self.regex.findall(value):
            raise ValidationError(
                message='Username содержит некорректные символы.')
        return value
