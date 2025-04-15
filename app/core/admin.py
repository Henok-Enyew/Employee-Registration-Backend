from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee, EmployeeAddress, EmployeeFamily

class EmployeeFamilyInline(admin.StackedInline):
    model = EmployeeFamily
    extra = 1  
    verbose_name_plural = 'Family Members'
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'relation'),
                ('birthdate',),
            )
        }),
    )
    list_filter = ('relation')
    search_fields = ('first_name', 'employee')
    
        
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('employee') 
class EmployeeAddressInline(admin.StackedInline):
    model = EmployeeAddress
    can_delete = False
    verbose_name_plural = 'Address Information'
    fieldsets = (
        (None, {
            'fields': (
                ('kebele', 'city'),
                ('pobox', 'birth_place'),
                ('home_number',),
                ('office_phone_number', 'home_phone_number'),
            )
        }),
    )

class EmployeeAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'role','is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'marital_status','age')}),
        ('Work Info', {'fields': ('department', 'position', 'salary','role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'verified_at')}),
    )
    inlines = (EmployeeAddressInline,EmployeeFamilyInline)

admin.site.register(Employee, EmployeeAdmin)