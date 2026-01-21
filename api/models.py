from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager 

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