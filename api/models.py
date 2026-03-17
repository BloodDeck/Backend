from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager 
from django.conf import settings

class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    ROLE_CHOICES = (
        ('admin', 'Super Admin'),
        ('hospital', 'Hospital'),
        ('donor', 'Donor'),
        ('bloodbank', 'Blood Bank'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='donor')
    
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] 

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} - {self.role}"
    
class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    applicant_name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=(('bloodbank', 'Blood Bank'), ('hospital', 'Hospital')))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.applicant_name} - {self.status}"

class Inventory(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inventory', limit_choices_to={'role__in': ['hospital', 'bloodbank']})
    blood_group = models.CharField(max_length=3) # e.g., A+, B-, O+
    units = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Inventories"
        unique_together = ('owner', 'blood_group')

    def __str__(self):
        return f"{self.owner.get_full_name()} - {self.blood_group}: {self.units} units"

class Donation(models.Model):
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donations', limit_choices_to={'role': 'donor'})
    location = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='hosted_donations', limit_choices_to={'role__in': ['hospital', 'bloodbank']})
    blood_group = models.CharField(max_length=3)
    units = models.PositiveIntegerField(default=1)
    
    # 1. Removed auto_now_add=True so donors can pick future dates
    donation_date = models.DateField() 
    
    # 2. Changed default to 'scheduled' instead of 'completed'
    status = models.CharField(max_length=20, default='scheduled') 

    def __str__(self):
        return f"Donation by {self.donor.email} on {self.donation_date}"
    
class InventoryLog(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='logs')
    action_type = models.CharField(max_length=20) 
    amount = models.PositiveIntegerField()
    source = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.action_type} - {self.amount} units for {self.inventory.owner.email}"