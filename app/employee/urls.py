"""
URL mapping for employee api
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmployeeViewSet,
    SendOTPView,
    CustomTokenObtainPairView,
    EmployeeAddressViewSet,
    EmployeeFamilyViewSet,
    CurrentEmployeeAddressView,
    CurrentEmployeeFamilyView,
    VerifyEmailAndSetPasswordView
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
    path('signup/', SendOTPView.as_view({'post': 'signup'}), name="signup"),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('employee/<uuid:employee_id>/address', employee_address, name='employee-address'),
    path('employee/<uuid:employee_id>/family/', family_viewset, name='employee-family'),
    path('employee/<uuid:employee_id>/family/<int:pk>', 
        EmployeeFamilyViewSet.as_view({'patch': 'update_family'}),
        name='employee-family-update'),
    path('employee/<uuid:employee_id>/family/<int:pk>', 
        EmployeeFamilyViewSet.as_view({'delete': 'delete_family'}),
        name='employee-family-delete'),
    
    path('verify-email/', VerifyEmailAndSetPasswordView.as_view({'post':'verify_email_and_set_password'}), name='erify_email_and_set_password'),
    path('employee/me/address', CurrentEmployeeAddressView.as_view({
        'get':'get_my_address'
    }), name="get_my_address"),
    path('employee/me/family', CurrentEmployeeFamilyView.as_view({
        'get':'get_my_families'
    }), name="get_my_family")   

]