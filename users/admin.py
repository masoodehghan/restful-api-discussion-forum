from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('point',)}),
    )
    readonly_fields = UserAdmin.readonly_fields + ('point',)


admin.site.register(User, CustomUserAdmin)
