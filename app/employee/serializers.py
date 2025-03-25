"""
Serialiazers for employee API
"""

from rest_framework import serializers
from core.models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""


    class Meta:
        model = Employee
        fields = ['id','first_name', 'last_name', 'age','sex','phone_number','position','salary','hire_date']
        read_only_fields = ['id']