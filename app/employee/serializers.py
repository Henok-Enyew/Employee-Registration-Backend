from rest_framework import serializers
from core import models

class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model"""

    class Meta:
        model = models.Employee
        fields = '__all__'
