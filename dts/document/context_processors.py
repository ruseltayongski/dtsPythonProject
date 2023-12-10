from .models import Document
from django.db.models import Q


def document_count(request):
    if request.user.is_authenticated:
        count = Document.objects.filter(created_by__department=request.user.department).count()
    else:
        count = 0
    return {'document_count': count}


def incoming_document_count(request):
    if request.user.is_authenticated:
        count = (Document.objects
                 .filter(
                        Q(released_to=request.user.department, status='released') |
                        Q(returned_to=request.user.department, status='returned')
                    )
                 .count())
    else:
        count = 0
    return {'incoming_document_count': count}


def outgoing_document_count(request):
    if request.user.is_authenticated:
        count = Document.objects.filter(accepted_by=request.user.department, status='accepted').count()
    else:
        count = 0
    return {'outgoing_document_count': count}


def cycle_end_document_count(request):
    if request.user.is_authenticated:
        count = Document.objects.filter(cycle_end_by=request.user.department, status='cycled end').count()
    else:
        count = 0
    return {'cycle_end_document_count': count}
