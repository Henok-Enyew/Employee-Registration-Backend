from rest_framework import serializers
from core.models import Employee
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import check_password

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id','username','email',    'first_name','middle_name','last_name','phone_number',    'department','position','salary','hire_date',    'state','citizenship','sex','created_at']
        extra_kwargs = {
            'password': {'write_only': True},
             'created_at': {'read_only': True}
        }

    def create(self, validated_data):
        validated_data.pop('password',None)
        employee = Employee.objects.create_user(
            **validated_data
        )

        return employee
    def update(self, instance, validated_data):
        validated_data.pop('password',None)
        return super().update(instance,validated_data)
         
        

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        token['username'] = user.username
        token['role'] = user.role
        default_pattern = f"{user.username.lower()}@1234"  
        if check_password(default_pattern, user.password):
            token['requires_password_change'] = True
            
        return token    

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    def validate_current_password(self, value):
        employee = self.context['request'].user
        if not employee.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value