from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import Employee
from employee.serializers import EmployeeSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    # Link User to Employee by using `employee` as a ForeignKey
    employee = EmployeeSerializer()

    class Meta:
        model = get_user_model()  # Automatically uses the custom user model (User)
        fields = ['id', 'employee', 'role', 'is_active', 'is_staff', 'is_superuser', 'password']

    def create(self, validated_data):
        employee_data = validated_data.pop('employee')
        employee = Employee.objects.create(**employee_data)  # Create the related employee instance
        
        user = get_user_model().objects.create_user(
            employee=employee,
            password=validated_data['password'],
            role=validated_data['role'],
            is_active=validated_data['is_active'],
            is_staff=validated_data['is_staff'],
            is_superuser=validated_data['is_superuser']
        )
        
        return user

    def update(self, instance, validated_data):
        employee_data = validated_data.pop('employee')
        # Update the related Employee model
        instance.employee.first_name = employee_data.get('first_name', instance.employee.first_name)
        instance.employee.last_name = employee_data.get('last_name', instance.employee.last_name)
        instance.employee.save()

        # Now update User model itself
        instance.role = validated_data.get('role', instance.role)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.is_superuser = validated_data.get('is_superuser', instance.is_superuser)

        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        
        instance.save()
        return instance

class TokenObtainPairSerializer(serializers.Serializer):
    """Custom serializer for token generation"""
    refresh = serializers.CharField()
    access = serializers.CharField()

    def validate(self, attrs):
        user = self.context['request'].user
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
