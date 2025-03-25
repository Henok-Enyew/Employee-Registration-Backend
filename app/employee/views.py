"""
Views for employee API
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Employee
from employee import serializers


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.EmployeeSerializer
    queryset = Employee.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve Employees for authenticated user
        """
        return self.queryset.order_by('-id')
    
    # def perform_create(self):
    #     """Create new Employee"""
    #     serializers.save(user=self.)