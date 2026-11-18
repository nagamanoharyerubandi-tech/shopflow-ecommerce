from django.contrib import admin
from .models import UserProfile, Address


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'gender', 'date_of_birth', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'city', 'state', 'postal_code', 'is_default')
    list_filter = ('is_default', 'address_type', 'city', 'state')
    search_fields = ('user__username', 'full_name', 'phone', 'postal_code', 'city')
