from django.contrib import admin
from .models import User, Application, Inventory, Donation, InventoryLog

# Unregister if already registered
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# --- REGISTER USER MODEL ---
@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin): # Note: We are using ModelAdmin now, not UserAdmin!
    list_display = ('email', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    # We define ONE layout for both adding and editing users
    fieldsets = (
        ('Authentication', {'fields': ('email', 'password')}),
        ('Personal Information', {'fields': ('first_name', 'last_name', 'phone_number', 'address', 'city')}),
        ('BloodDeck Specifics', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    def save_model(self, request, obj, form, change):
        # SECURITY: Check if the password is plain text. If it is, hash it!
        # (Hashes always start with 'pbkdf2_sha256', so we check for that)
        if obj.password and not obj.password.startswith('pbkdf2_sha256'):
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


# --- REGISTER APPLICATION MODEL ---
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant_name', 'category', 'status', 'user', 'created_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('applicant_name', 'user__email')
    ordering = ('-created_at',)
    list_editable = ('status',) 


# --- REGISTER INVENTORY MODEL ---
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('owner', 'blood_group', 'units', 'last_updated')
    list_filter = ('blood_group',)
    search_fields = ('owner__email', 'owner__first_name')
    ordering = ('-last_updated',)
    list_editable = ('units',) 


# --- REGISTER DONATION MODEL ---
@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'blood_group', 'units', 'location', 'status', 'donation_date')
    list_filter = ('status', 'blood_group', 'donation_date')
    search_fields = ('donor__email', 'location__email')
    ordering = ('-donation_date',)
    list_editable = ('status',)

@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('inventory', 'action_type', 'amount', 'source', 'user', 'date')
    list_filter = ('action_type', 'date')
    search_fields = ('inventory__owner__email', 'inventory__owner__first_name', 'source', 'user__email')
    ordering = ('-date',)

    # SECURITY: Make the ledger completely read-only to prevent tampering!
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
        
    def has_delete_permission(self, request, obj=None):
        return False