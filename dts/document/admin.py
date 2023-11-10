from django.contrib import admin

# Register your models here.

from .models import Position, Department, Employee, Document, Tracking, Feedback

admin.site.register(Position)
admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(Document)
admin.site.register(Tracking)
admin.site.register(Feedback)
