# Register your models here.
# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm



class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('course', 'year')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('course', 'year')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

# users/admin.py


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('course', 'year')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('course', 'year')}),
    )
