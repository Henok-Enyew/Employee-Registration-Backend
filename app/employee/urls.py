"""
URL mapping for employee api
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmployeeViewSet,
    CustomTokenObtainPairView,
    EmployeeAddressViewSet,
    EmployeeFamilyViewSet,
    VerifyEmailView
)

router = DefaultRouter()
router.register(r'employee', EmployeeViewSet, basename='employee')

employee_address = EmployeeAddressViewSet.as_view({
    'get': 'retrieve',
    'post': 'create',
    'patch': 'partial_update',
    'delete': 'destroy',
})

family_viewset = EmployeeFamilyViewSet.as_view({
    'get': 'get_all_family',
    'post': 'add_family',

})

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('employee/<uuid:employee_id>/address', employee_address, name='employee-address'),
    path('employee/<uuid:employee_id>/family/', family_viewset, name='employee-family'),
    path('employee/<uuid:employee_id>/family/<int:pk>', 
        EmployeeFamilyViewSet.as_view({'patch': 'update_family'}),
        name='employee-family-update'),
    path('employee/<uuid:employee_id>/family/<int:pk>', 
        EmployeeFamilyViewSet.as_view({'delete': 'delete_family'}),
        name='employee-family-delete'),
    
    path('auth/verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    
]