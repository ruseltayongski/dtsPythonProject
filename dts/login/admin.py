from django.contrib import admin

# Register your models here.

from .models import (Employee, Position, Department)


admin.site.register(Position)
admin.site.register(Department)
admin.site.register(Employee)
