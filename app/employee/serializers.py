from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from core.models import Employee, EmployeeAddress, EmployeeFamily
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import PermissionDenied
from datetime import datetime

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id','username','email','first_name','middle_name','last_name','mother_name','phone_number','role','department','position','salary','hire_date',    'state','citizenship','sex','created_at', 'birthdate','marital_status', 'is_verified']
        extra_kwargs = {
            'password': {'write_only': True},
            'created_at': {'read_only': True},
            'is_verified': {'read_only': True}
        }

    def create(self, validated_data):
        validated_data.pop('password',None)
        validated_data.pop('role',None)
        employee = Employee.objects.create_user(
            **validated_data
        )
        return employee
    def update(self, instance, validated_data):
        validated_data.pop('password',None)
        validated_data.pop('role',None)
        return super().update(instance,validated_data)


class EmployeeSignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True) 
    class Meta:
        model = Employee
        fields = ['email']  
        extra_kwargs = {
            'email': {'write_only': True}  
        }


class VerifyEmailAndSetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = Employee
        fields = ['email','otp_secret','password', 'password_confirm']
        extra_kwargs = {
            'email': {'write_only':True}
        }
    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError("The passwords didn't match.")

        return attrs
    def update(self, instance, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)

        instance.is_verified = True
        instance.verified_at = datetime.now()
        if password:
            instance.set_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class CurrentEmployeeAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAddress
        fields = "__all__"


class CurrentEmployeeFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeFamily
        fields = "__all__"

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        employee = self.user
        print(employee)
        if not employee.is_verified:
            raise PermissionDenied("Please verify your email address to log in.")

        default_pattern = f"{employee.username.lower()}@1234"
        if check_password(default_pattern, employee.password):
            return {
                'access_token': data['access'],
                'refresh_token': data['refresh'],
                'changedefaultpassword': True  
            }
        return {
            'access_token': data['access'],
            'refresh_token': data['refresh'],
        }


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    def validate_current_password(self, value):
        employee = self.context['request'].user
        if not employee.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value
    

class EmployeeAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAddress
        fields = ['kebele', 'city', 'pobox', 'office_phone_number','home_phone_number','home_number','birth_place']

class EmployeeFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeFamily
        fields = ['id','name','birthdate','relation']



# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
        
#         token['username'] = user.username
#         token['role'] = user.role
#         default_pattern = f"{user.username.lower()}@1234"  
#         if check_password(default_pattern, user.password):
#             data = {
#                     "message": "The employee need to change his defualt password",
#                     "status": "success",
#                     "data": {
#                         None
#                     }
#                 }
#             return Response(data,status=status.HTTP_200_OK) 
#             # token['requires_password_change'] = True
#         return token    
        