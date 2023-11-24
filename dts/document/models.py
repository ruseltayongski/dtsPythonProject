from django.db import models


class Document(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey('login.Employee', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title


class Tracking(models.Model):
    remarks = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey('login.Employee', on_delete=models.SET_NULL, null=True, related_name='created_trackings')
    released_to = models.ForeignKey('login.Department', on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey('login.Employee', on_delete=models.SET_NULL, null=True, related_name='approved_trackings')

    def __str__(self):
        return self.remarks


class Feedback(models.Model):
    message = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey('login.Employee', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.message

