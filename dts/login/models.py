from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Position(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Department(models.Model):
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description


class Employee(AbstractUser):
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
