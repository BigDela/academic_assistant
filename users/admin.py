# Register your models here.
# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('course', 'year')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('course', 'year')}),
    )


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'program_of_study', 'year_level', 'theme_preference', 'updated_at']
    list_filter = ['theme_preference', 'created_at']
    search_fields = ['user__username', 'program_of_study']
    readonly_fields = ['created_at', 'updated_at']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

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
