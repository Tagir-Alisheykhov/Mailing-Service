from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'is_email_verified',
        'phone_number',
        'avatar',
        'token'
    ]
    list_filter = [
        'is_email_verified',
        'email'
    ]
    search_fields = [
        'email',
        'phone_number'
    ]
