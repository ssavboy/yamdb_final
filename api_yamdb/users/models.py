from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .mixins import UsernameValidatorMixin

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLES = ((USER, 'User'),
         (ADMIN, 'Moderator'),
         (MODERATOR, 'Admin'))


class User(AbstractUser, UsernameValidatorMixin):
    username = models.CharField(
        max_length=settings.RESTRICT_NAME,
        unique=True)
    email = models.EmailField(
        max_length=settings.RESTRICT_EMAIL,
        unique=True)
    first_name = models.CharField(
        verbose_name='Имя пользователя.',
        max_length=settings.RESTRICT_NAME,
        blank=True,
        null=True)
    last_name = models.CharField(
        verbose_name='Фамилия пользователя.',
        max_length=settings.RESTRICT_NAME,
        blank=True,
        null=True)
    bio = models.TextField(
        blank=True,
        null=True)
    role = models.CharField(
        max_length=max([len(value) for key, value in ROLES]),
        choices=ROLES,
        default=USER,
        blank=True)
    confirmation_code = models.TextField(
        unique=True,
        blank=True,
        null=True)

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return self.username
