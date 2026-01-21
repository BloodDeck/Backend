from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Super Admin'),
        ('hospital', 'Hospital'),
        ('donor', 'Donor'),
        ('bloodbank', 'Blood Bank'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='donor')

    def __str__(self):
        return f"{self.username} - {self.role}"