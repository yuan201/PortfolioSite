import factory
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = 'UserFactory'
    email = 'test@example.com'
    password = make_password('password')
