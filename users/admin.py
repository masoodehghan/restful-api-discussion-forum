from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    
    model = User
    list_display = ('email', 'is_active', 'is_staff', 'first_name', 'last_name')
    
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active', 'first_name', 'last_name')}
        ),
    )
    
    search_fields = ('email',)
    ordering = ('email',)
    
    

admin.site.register(User, CustomUserAdmin)


