from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

def validate_email(value):
    if User.objects.filter(email = value).exists():
        raise ValidationError(
            (f"The Email Address- {value} is already taken.Please choose another."),
            params = {'value':value}
        )


def validate_username(value):
    if User.objects.filter(username = value).exists():
        raise ValidationError(
            (f"The UserName- {value} is already taken.Please choose another."),
            params = {'value':value}
        )


def validate_password(value):
    if User.objects.filter('password1') != User.objects.filter('password2'):
        raise ValidationError('Two Password Fields did not match. Try again')
