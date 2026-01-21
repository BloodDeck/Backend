from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # This list controls the columns you see in the main table
    list_display = ('email', 'role', 'is_staff', 'is_active', 'date_joined')
    
    # This adds the filter sidebar on the right
    list_filter = ('role', 'is_staff', 'is_active')
    
    # This makes the email searchable
    search_fields = ('email',)
    
    # REQUIRED: Since we removed 'username', we must tell Admin to order by 'email'
    ordering = ('email',)

    # --- This part controls the "EDIT" page ---
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Information', {'fields': ('first_name', 'last_name')}),
        ('BloodDeck Specifics', {'fields': ('role',)}), # <--- Make sure 'role' is here!
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    # --- This part controls the "ADD USER" page ---
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'role', 'is_staff', 'is_active'),
        }),
    )

# Unregister if already registered (prevents "AlreadyRegistered" error)
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)