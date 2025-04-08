from rest_framework import viewsets, permissions, status,mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from core.models import Employee, EmployeeAddress
from .serializers import (EmployeeSerializer,
                           CustomTokenObtainPairSerializer,
                           PasswordChangeSerializer,
                             EmployeeAddressSerializer)
from .permissions import IsAdminUser
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.exceptions import NotFound, ValidationError

class EmployeeViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete','patch']
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get_permissions(self):
        if self.action in ['create','list', 'retrieve', 'update', 'partial_update', 'destroy','reset_password']:
            # Restrict all actions to admin only
            return [permissions.IsAuthenticated(), IsAdminUser()]
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
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class EmployeeAddressViewSet(viewsets.GenericViewSet,
                             mixins.RetrieveModelMixin,
                             mixins.CreateModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.DestroyModelMixin):
    serializer_class = EmployeeAddressSerializer
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
