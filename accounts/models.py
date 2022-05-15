from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):

    def get_queryset(self):
        return super().get_queryset()

    def create(self, **kwargs):
        password = kwargs.pop('password', None)
        user = self.model(**kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        userdata = {
            'email': email,
            'password': password
        }
        userdata.update(kwargs)
        user = self.create(**userdata)
        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.create_user(
            email,
            password=password,
            **kwargs
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    identifier_id = models.CharField('Identifier ID', max_length=10, null=True)
    email = models.EmailField('Email', unique=True)
    name = models.CharField('Name', max_length=150, blank=True)
    objects = UserManager()

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.email}'
