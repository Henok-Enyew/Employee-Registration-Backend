from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import uuid


class EmployeeManager(BaseUserManager):
    """Custom manager for Employee model"""
    
    def create_user(self, username, password=None, **extra_fields):
        """Create and save a regular Employee"""
        if not username:
            raise ValueError("Username is required")
        if password is None:
            password = f"{username.lower()}@1234" 
    
        if 'email' in extra_fields:
            extra_fields['email'] = self.normalize_email(extra_fields['email'])   
        employee = self.model(
            username=username, 
            **extra_fields
        )
        employee.set_password(password)
        employee.save(using=self._db)
        return employee

    def create_superuser(self, username, password,**extra_fields):
        """Create and save a superuser Employee"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(username, password,**extra_fields)

class Employee(AbstractBaseUser, PermissionsMixin):
    """Single model handling both authentication and employee data"""
    
    # Authentication fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    
    # Employee details
    first_name = models.CharField(max_length=30, blank=True, null=True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    
    # Employment info (all optional)
    department = models.CharField(max_length=25, blank=True, null=True)
    role = models.CharField(max_length=20, default='employee', blank=True)
    state = models.CharField(max_length=25, blank=True, null=True)
    citizenship = models.CharField(max_length=25, default='Ethiopia', blank=True)
    sex = models.CharField(max_length=10, blank=True, null=True)
    position = models.CharField(max_length=40, default='Unknown', blank=True)
    salary = models.IntegerField(null=True, blank=True)
    hire_date = models.DateTimeField(null=True, blank=True)

    objects = EmployeeManager()

    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.username} - {self.first_name} {self.last_name}"
