from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from .enums import RoleChoices, MaxLength, MaritalStatusChoices, RelationChoices
import uuid
from datetime import date
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

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
    username = models.CharField(max_length=MaxLength.USERNAME, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    otp_secret = models.CharField(max_length=32, null=True, blank=True) 
    
    # Employee details
    first_name = models.CharField(max_length=MaxLength.NAME, blank=True )
    middle_name = models.CharField(max_length=MaxLength.NAME, blank=True)
    last_name = models.CharField(max_length=MaxLength.NAME, blank=True)
    mother_name = models.CharField(max_length=MaxLength.NAME, blank=True)
    phone_number = models.CharField(max_length=MaxLength.PHONE_NUMBER, blank=True)
    email = models.EmailField(max_length=MaxLength.EMAIL, unique=True, blank=True)
    
    # Employment info (all optional)
    department = models.CharField(max_length=MaxLength.DEPARTMENT, blank=True)
    role = models.CharField(max_length=MaxLength.ROLE,choices=RoleChoices.choices,  default=RoleChoices.EMPLOYEE)
    state = models.CharField(max_length=MaxLength.STATE, blank=True, null=True)
    citizenship = models.CharField(max_length=MaxLength.CITIZENSHIP, default='Ethiopia', blank=True)
    sex = models.CharField(max_length=MaxLength.SEX, blank=True, null=True)
    age = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(100)], null=True )
    marital_status = models.CharField(max_length=MaxLength.MARITAL_STATUS, choices=MaritalStatusChoices.choices, null=True)

    position = models.CharField(max_length=MaxLength.POSITION, default='Unknown', blank=True)
    salary = models.IntegerField(null=True, blank=True)

    hire_date = models.DateField(null=True, blank=True)
    retirement_date = models.DateField(null=True,blank=True)
    birthdate = models.DateField(null=True,blank=True)

    objects = EmployeeManager()

    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    def save(self,*args, **kwargs):
        if self.birthdate:
            retirement_age = 60
            retirement_year = self.birthdate.year + retirement_age
            today = date.today()
            self.age = today.year - self.birthdate.year -  ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
            self.retirement_date = date(retirement_year,self.birthdate.month, self.birthdate.day)
        
        super().save(*args,**kwargs)

    def __str__(self):
        return f"{self.username} - {self.first_name} {self.last_name}"



class EmployeeAddress(models.Model):
    employee = models.OneToOneField(
        Employee, # could have been just Employee just to make dynamic dude?
        on_delete= models.CASCADE,
        related_name="address",
        primary_key=True
    )
    kebele = models.CharField(max_length=MaxLength.KEBELE,blank=True)
    city = models.CharField(max_length=MaxLength.CITY,blank=True)
    pobox = models.CharField(max_length=MaxLength.PO_BOX,blank=True)
    office_phone_number = models.CharField(max_length=MaxLength.PHONE_NUMBER,blank=True)
    home_phone_number = models.CharField(max_length=MaxLength.PHONE_NUMBER,blank=True)
    home_number = models.CharField(max_length=MaxLength.NAME, blank=True)
    birth_place = models.CharField(max_length=MaxLength.NAME, blank=True)

    def __str__(self):
        return str(self.employee)
    

class EmployeeFamily(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="family",
    )
    name = models.CharField(max_length=MaxLength.NAME*2)
    relation = models.CharField(max_length=MaxLength.NAME,choices=RelationChoices.choices ,blank=True)
    birthdate = models.DateField(null=True,blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.relation}) - {self.employee.first_name} {self.employee.last_name}"