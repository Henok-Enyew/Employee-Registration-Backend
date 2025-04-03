from rest_framework import serializers
from core.models import Employee
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
         
    # def update_password(self,instance,validated_data):
    #     password = validated_data.pop('password')
    #     employee = super().update(instance,validated_data)
    #     employee.set_password(password)
    #     employee.save()
        

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        print(user)
        token = super().get_token(user)

        token['username'] = user.username
        # token['is_admin'] = user.is_staff
        return token
    

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_current_password(self, value):
        employee = self.context['request'].user
        if not employee.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value