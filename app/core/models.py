from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import uuid

class Employee(models.Model):
    """Employee model for storing details"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.IntegerField(unique=True)  # Auto-incremented manually
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    state = models.CharField(max_length=25)
    citizenship = models.CharField(max_length=25, default='Ethiopia')
    sex = models.CharField(max_length=10)
    position = models.CharField(max_length=40, default='Unknown')
    salary = models.IntegerField()
    hire_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        """Auto-increment employee ID"""
        if not self.employee_id:
            last_employee = Employee.objects.order_by('-employee_id').first()
            self.employee_id = (last_employee.employee_id + 1) if last_employee else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name}"

class UserManager(BaseUserManager):
    """User manager"""

    def create_user(self, employee, password=None, **extra_fields):
        """Create and return a new user"""
        if not employee:
            raise ValueError("User must be linked to an employee.")
        user = self.model(employee=employee, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser"""
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    """User model for authentication"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="user")
    role = models.CharField(max_length=20,  default='employee')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'employee'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.employee.employee_id} - {self.role}"
