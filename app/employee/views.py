from rest_framework import viewsets, permissions, status,mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import UntypedToken
from core.models import Employee, EmployeeAddress, EmployeeFamily
from .serializers import (EmployeeSerializer,
                           CustomTokenObtainPairSerializer,
                           PasswordChangeSerializer,
                             EmployeeAddressSerializer,
                             EmployeeFamilySerializer)
from .permissions import IsHRManager,IsVerified
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.exceptions import NotFound, ValidationError
from django.utils import timezone

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


class VerifyEmailView(APIView):
    """
    Verify user email using JWT token
    """
    def get(self, request):
        token = request.query_params.get('token')
        
        if not token:
            return Response(
                {"error": "Verification token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validated_token = UntypedToken(token)
            user_id = validated_token['user_id']
            
            # Get user and verify
            user = Employee.objects.get(id=user_id)
            if user.is_verified:
                return Response(
                    {"message": "Email is already verified"},
                    status=status.HTTP_200_OK
                )
            
            # Mark as verified
            user.is_verified = True
            user.verified_at = timezone.now()  # Optional: track verification time
            user.save()
            
            return Response(
                {"message": "Email verified successfully!"},
                status=status.HTTP_200_OK
            )
            
        except (InvalidToken, TokenError) as e:
            return Response(
                {"error": "Invalid or expired verification link"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Employee.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class CustomTokenObtainPairView(TokenObtainPairView):
    """  View to log the user in"""
    serializer_class = CustomTokenObtainPairSerializer
    permissions_classes = [IsVerified]


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