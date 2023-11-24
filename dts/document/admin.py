from django.contrib import admin

# Register your models here.

from .models import (Document, Tracking, Feedback)


admin.site.register(Document)
admin.site.register(Tracking)
admin.site.register(Feedback)
