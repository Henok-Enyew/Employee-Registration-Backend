from django.db import models

class RoleChoices(models.TextChoices):
    HR_MANAGER = 'HR Manager'
    HR_OFFICER = 'HR Officer'
    EMPLOYEE = 'Employee'

class MaritalStatusChoices(models.TextChoices):
    SINGLE = 'Single', 'Single'
    MARRIED = 'Married', 'Married'
    DIVORCED = 'Divorced', 'Divorced'
    WIDOWED = 'Widowed', 'Widowed'
    SEPARATED = 'Separated', 'Separated'

class MaxLength:
    USERNAME = 50
    NAME = 30
    PHONE_NUMBER = 15
    EMAIL = 254  
    DEPARTMENT = 25
    ROLE = 20
    STATE = 25
    CITIZENSHIP = 25
    SEX = 10
    POSITION = 40
    AGE=2
    MARITAL_STATUS=20
    KEBELE=50
    CITY=50
    PO_BOX=20