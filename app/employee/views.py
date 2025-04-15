from rest_framework import viewsets, permissions, status,mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import UntypedToken
from core.models import Employee, EmployeeAddress, EmployeeFamily
from .utils import generate_otp, verify_otp, send_verification_email
from .serializers import (EmployeeSerializer,
                           CustomTokenObtainPairSerializer,
                           PasswordChangeSerializer,
                             EmployeeAddressSerializer,
                             EmployeeFamilySerializer,
                             CurrentEmployeeAddressSerializer,
                             CurrentEmployeeFamilySerializer,
                             EmployeeSignUpSerializer,
                             VerifyEmailAndSetPasswordSerializer)
from .permissions import IsHRManager,IsVerified
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.exceptions import NotFound, ValidationError
from django.utils import timezone
from datetime import date

class EmployeeViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete','patch']
    queryset = Employee.objects.filter(is_staff=False)
    serializer_class = EmployeeSerializer
    def get_permissions(self):
        if self.action in ['create','list', 'retrieve', 'update', 'partial_update', 'destroy','reset_password']:
            """ Restrict all actions to admin only """
            return [permissions.IsAuthenticated(), IsHRManager()]
        return [permissions.IsAuthenticated()] # 
    
    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """
        Admin resets an employee's password by sending an employee_id in the request body.
        """
        employee_id = request.data.get("employee_id") 
        if not employee_id:
            return Response({"error": "Employee ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.get(id=employee_id)
            password = f"{employee.username.lower()}@1234" 
            employee.set_password(password) 
            employee.save()
            return Response({"status": "Password reset successfully"}, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)



    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        instance = request.user
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({"status": "password updated"}, status=status.HTTP_200_OK)


class SendOTPView(viewsets.GenericViewSet):
    serializer_class = EmployeeSignUpSerializer
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def signup(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            employee = Employee.objects.get(email = email)
            if employee.is_verified:
                return Response({'message': "You are already verified, Login to your account"})
            totp = generate_otp()
            employee.otp_secret = totp
            send_verification_email(employee)
            employee.save()
            return Response({'message': "The OTP has been sent"} ,status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            raise NotFound("Employee with that email does not exist!")
           

class VerifyEmailAndSetPasswordView(viewsets.GenericViewSet):
    """Verify OTP, set Password"""    
    serializer_class = VerifyEmailAndSetPasswordSerializer
    @action(detail=False, method=['post'], permission_classes=[permissions.AllowAny])
    def verify_email_and_set_password(self, request):
        email = request.data.get("email")
        try:
            employee = Employee.objects.get(email = email)
            if employee.is_verified:
                return Response({'message': "The user with this email already verified niggah"}, status=status.HTTP_400_BAD_REQUEST)
        except Employee.DoesNotExist:
            raise NotFound("Employee with that email does not exist!")
        serializer = self.get_serializer(instance=employee, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        otp_from_user = serializer.validated_data['otp_secret']
        otp = employee.otp_secret
        is_otp_correct = verify_otp(otp, otp_from_user)
        
        if is_otp_correct:
            serializer.save()  
            return Response({'message': "Account verified successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({'message': "The OTP didn't match or expired"}, status=status.HTTP_400_BAD_REQUEST)

class CurrentEmployeeAddressView(viewsets.GenericViewSet):
    """ Getting the address of currently authenticated employee"""

    serializer_class = CurrentEmployeeAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    @action(detail=False, methods=['get'], url_path='get_my_address')
    def get_my_address(self, request):
        employee_id = request.user.id
        try:
            employee = Employee.objects.get(id=employee_id)
            address = employee.address
            serializer = self.get_serializer(address)
            if not address:
                return Response({'message': "The address of the employee has not been set yet"}, status.HTTP_404_NOT_FOUND)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            raise NotFound("Employee with that id does not exist!")


class CurrentEmployeeFamilyView(viewsets.GenericViewSet):
    """ Get the family memebers of currently authenticated employee"""

    serializer_class = CurrentEmployeeFamilySerializer
    permission_classes = [permissions.IsAuthenticated]
    @action(detail=False, methods=['get'], url_path='get_my_families')
    def get_my_families(self, request):
        employee_id = request.user.id
        try:
            employee = Employee.objects.get(id=employee_id)
            family_members = employee.family
            serializer = self.get_serializer(family_members, many=True)
            if not family_members:
                return Response({'message': "The Family Members of the employee has not been set yet"}, status.HTTP_404_NOT_FOUND)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            raise NotFound("Employee with that id does not exist!")
           

class CustomTokenObtainPairView(TokenObtainPairView):
    """  View to log the user in"""
    serializer_class = CustomTokenObtainPairSerializer
    # permission_classes = [IsVerified]


class EmployeeAddressViewSet(viewsets.GenericViewSet,
                             mixins.RetrieveModelMixin,
                             mixins.CreateModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.DestroyModelMixin):
    """View to manage employee address"""
    serializer_class = EmployeeAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'employee_id'

    def get_queryset(self):
        return EmployeeAddress.objects.select_related('employee')

    def get_object(self):
        employee_id = self.kwargs.get('employee_id')
        try:
            employee = Employee.objects.get(id=employee_id)
            return employee.address
        except Employee.DoesNotExist:
            raise NotFound("Employee with that id does not exist!")
        except EmployeeAddress.DoesNotExist:
            raise NotFound("The address of the employee has not been set yet! :(")

    def perform_create(self, serializer):
        employee_id = self.kwargs.get('employee_id')
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            raise NotFound("Employee with that id does not exist!")

        if hasattr(employee, 'address'):
            raise ValidationError("Address already exists for this employee.")

        serializer.save(employee=employee)


class EmployeeFamilyViewSet(viewsets.GenericViewSet):
    """
    Viewset for managing employee familes
    """
    queryset = EmployeeFamily.objects.all() 
    serializer_class = EmployeeFamilySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'employee_id'
    def get_queryset(self):
        employee_id = self.kwargs.get('employee_id')
        return EmployeeFamily.objects.filter(employee__id=employee_id)
    
    @action(detail=False, methods=['get'], url_path='get_all_family')
    def get_all_family(self,request,*args, **kwargs):
        """ Retireve all family members of an employee"""
        employee_id = kwargs.get('employee_id') 
        try:
            employee = Employee.objects.get(id=employee_id)
            family_members = employee.family
            serializer = self.get_serializer(family_members, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)            
        except Employee.DoesNotExist:
            raise NotFound("Employee with that id does not exist!")
        except EmployeeFamily.DoesNotExist:
            raise NotFound("The family of the employee has not been set yet! :(")
    
    
    @action(detail=False, methods=['post'],  url_path='add_family')
    def add_family(self, request, employee_id=None):
        """ Add a family member to an employee """
        # employee_id = self.kwargs.get('employee_id')
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            raise NotFound("Employee with that id does not exist!")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(employee=employee)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'],url_path='update_family')
    def update_family(self, request, employee_id=None, pk=None):
        """ Update a family member of an employee """
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            raise NotFound("Employee with that id does not exist!")

        family_member = get_object_or_404(EmployeeFamily, id=pk, employee=employee)
        serializer = self.get_serializer(family_member, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['delete'],url_path='delete_family')
    def delete_family(self,request,employee_id=None, pk=None):
        """ Delete a family member of an employee """
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            raise NotFound("Employee with that id does not exist!")

        family_member = get_object_or_404(EmployeeFamily, id=pk, employee=employee)
        family_member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)