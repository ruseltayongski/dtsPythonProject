from django.db import models
from random import randint
from datetime import datetime


class Document(models.Model):
    route_no = models.CharField(max_length=255, null=True)
    title = models.CharField(max_length=255, null=True)
    content = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=255, null=True)
    created_by = models.ForeignKey('login.Employee', on_delete=models.SET_NULL, null=True, related_name='created_document')
    released_to = models.ForeignKey('login.Department', on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey('login.Employee', on_delete=models.SET_NULL, null=True, related_name='approved_document')
    accepted_by = models.ForeignKey('login.Department', on_delete=models.SET_NULL, null=True,
                                    related_name='accepted_document')
    cycle_end_by = models.ForeignKey('login.Department', on_delete=models.SET_NULL, null=True,
                                    related_name='cycle_end_document')
    returned_to = models.ForeignKey('login.Department', on_delete=models.SET_NULL, null=True,
                                    related_name='returned_document')
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        if self.pk is None:
            current_user_id = self.created_by.id if self.created_by else 'unknown'
            timestamp = datetime.now().strftime('%m%d%H%M%S')
            random_numbers = ''.join(str(randint(1, 9)) for _ in range(3))
            self.route_no = f"{datetime.now().strftime('%Y-')}{current_user_id}{timestamp}{random_numbers}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Tracking(models.Model):
    route_no = models.CharField(max_length=255, null=True)
    remarks = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255, null=True)
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey('login.Employee', on_delete=models.SET_NULL, null=True, related_name='created_trackings')
    released_to = models.ForeignKey('login.Department', on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey('login.Employee', on_delete=models.SET_NULL, null=True, related_name='approved_trackings')
    accepted_by = models.ForeignKey('login.Department', on_delete=models.SET_NULL, null=True,
                                    related_name='accepted_trackings')
    cycle_end_by = models.ForeignKey('login.Department', on_delete=models.SET_NULL, null=True,
                                     related_name='cycle_end_tracking')
    returned_to = models.ForeignKey('login.Department', on_delete=models.SET_NULL, null=True,
                                     related_name='returned_tracking')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.status


class Feedback(models.Model):
    message = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey('login.Employee', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.message

