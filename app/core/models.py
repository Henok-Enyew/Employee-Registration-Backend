"""
Models for Database
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)


class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self,email, password:None, **extra_fields):
        "Create, save and return new users"
        if not email:
            raise ValueError("User must have an email address.")
        user = self.model(email=self.normalize_email(email),**extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    

    def create_superuser(self,email,password):
        "Create and return superuser"

        user = self.create_user(email,password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Employee(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    age = models.IntegerField()
    sex = models.CharField(max_length=5)
    phone_number = models.CharField(max_length=15)
    position = models.CharField(max_length=40,default='Unknown')
    salary = models.IntegerField()
    hire_date=models.DateTimeField()
    
    def __str__(self):
        return self.first_name