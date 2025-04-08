"""
URL mapping for employee api
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, CustomTokenObtainPairView,EmployeeAddressViewSet

router = DefaultRouter()
router.register(r'employee', EmployeeViewSet, basename='employee')

employee_address = EmployeeAddressViewSet.as_view({
    'get': 'retrieve',
    'post': 'create',
    'patch': 'partial_update',
    'delete': 'destroy',
})



urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('employee/<uuid:employee_id>/address', employee_address, name='employee-address'),
]