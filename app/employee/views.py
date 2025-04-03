from rest_framework import viewsets, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from core.models import Employee
from .serializers import EmployeeSerializer, CustomTokenObtainPairSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()] 
        return super().get_permissions()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer