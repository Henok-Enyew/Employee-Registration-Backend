"""Django admin customization"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core import models

class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['employee', 'role', 'is_active']
    
    fieldsets = (
        (None, {'fields': ('employee', 'password')}),
        (_('Role & Permissions'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )

    readonly_fields = ['last_login']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'employee',
                'password1',
                'password2',
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )

class EmployeeAdmin(admin.ModelAdmin):
    """Admin page for employees"""
    ordering = ['employee_id']
    list_display = ['employee_id', 'first_name', 'last_name', 'email', 'position', 'hire_date']
    search_fields = ['first_name', 'last_name', 'email']
    list_filter = ['position', 'hire_date']

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Employee, EmployeeAdmin)
