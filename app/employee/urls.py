"""
URL mapping for employee api
"""

from django.urls import (path, include)

from rest_framework.routers import DefaultRouter

from employee import views
from .views import EmployeeViewSet

# router = DefaultRouter()
# router.register('employees', views.EmployeeViewSet)

# app_name ='employee'

# urlpatterns = [
#     path('',include(router.urls)),
# ]
router = DefaultRouter()
router.register(r'employee', views.EmployeeViewSet, basename='employee')

urlpatterns = [
    path('list/', include(router.urls)),  
]
