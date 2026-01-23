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