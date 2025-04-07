"""
URL mapping for employee api
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, CustomTokenObtainPairView, EmployeeAddressViewset

router = DefaultRouter()
router.register(r'employee', EmployeeViewSet, basename='employee')

employee_address_router = DefaultRouter()
employee_address_router.register(r'address', EmployeeAddressViewset, basename="employee_address")

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('employee/<uuid:employee_id>/',include(employee_address_router.urls))
]