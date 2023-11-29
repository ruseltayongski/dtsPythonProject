from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import DocumentForm
from .models import Document, Tracking
from django.db.models import Q
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone


# Create your views here.

@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')


@login_required(login_url='login')
def documents(request):
    query = request.GET.get('q')
    data = Document.objects.all()

    if query:
        data = data.filter(Q(route_no__icontains=query))

    data = data.order_by('-id')

    items_per_page = 3
    paginator = Paginator(data, items_per_page)

    page = request.GET.get('page')
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    return render(request, 'documents.html', {'documents': data, 'query': query})


def create_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST)
        if form.is_valid():
            document = form.save(commit=False)

            document.created_by = request.user
            document.status = "created"
            document.save()

            Tracking.objects.create(
                route_no=document.route_no,
                status=document.status,
                document=document,
                created_by=document.created_by,
                remarks=document.title
            )

            messages.success(request, 'Successfully saved document!')

            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = DocumentForm()

    return render(request, 'create_documents.html', {'form': form})


def update_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    if request.method == 'POST':
        form = DocumentForm(request.POST, instance=document)
        if form.is_valid():
            document = form.save(commit=False)
            document.save()

            messages.success(request, 'Successfully updated document!')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = DocumentForm(instance=document)

    return render(request, 'info_documents.html', {'form': form, 'document': document})


def get_duration(created):
    now = timezone.now()
    delta = now - created

    if delta.total_seconds() < 60:
        return 'moments ago'
    elif delta.total_seconds() < 3600:
        minutes = int(delta.total_seconds() / 60)
        return f'{minutes} {"minute" if minutes == 1 else "minutes"} ago'
    elif delta.total_seconds() < 86400:
        hours = int(delta.total_seconds() / 3600)
        return f'{hours} {"hour" if hours == 1 else "hours"} ago'
    elif delta.total_seconds() < 2592000:  # 30 days
        days = int(delta.total_seconds() / 86400)
        return f'{days} {"day" if days == 1 else "days"} ago'
    else:
        months = int(delta.total_seconds() / 2592000)
        return f'{months} {"month" if months == 1 else "months"} ago'


def track_document(request, pk):
    query = Q()
    if pk.isdigit():
        pk_value = int(pk)
        query |= Q(document_id=pk_value)
    else:
        pk_value = pk
        query |= Q(route_no=pk_value)

    tracking = Tracking.objects.filter(query).all()

    for track in tracking:
        track.duration = get_duration(track.created)

    return render(request, 'track_documents.html', {'tracking': tracking})
