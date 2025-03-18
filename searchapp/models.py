# Create your models here.

from django.contrib.auth.models import AbstractUser
from djongo import models

class CompanyInfo(models.Model):
    company_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'pep_company_info'


class LoginCredentials(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)  # Store hashed passwords
    role = models.CharField(max_length=50)  # superadmin, admin, or user

    def __str__(self):
        return self.username


class User(AbstractUser):
    ROLE_CHOICES = (
        ('superadmin', 'Superadmin'),
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
