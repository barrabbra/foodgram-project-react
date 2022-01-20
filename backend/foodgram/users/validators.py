from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class MaximumLengthValidator:
    def __init__(self, max_length=150):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) < self.max_length:
            raise ValidationError(
                _(
                    f'This password must contain at '
                    f'more %(min_length)d characters.'
                ),
                code='password_too_long',
                params={'max_length': self.max_length},
            )

    def get_help_text(self):
        return _(
            'Your password must contain at more %(max_length)d characters.'
            % {'max_length': self.max_length}
        )
