from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import DocumentForm
from .models import Document, Tracking
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from login.models import Department
from django.db.models import Count, F
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from django.http import JsonResponse


# Create your views here.

@login_required(login_url='login')
def home(request):
    current_user = request.user

    trackings = Tracking.objects.filter(created_by=request.user.id, document_id__isnull=False).all().order_by('-id')
    items_per_page = 4
    paginator = Paginator(trackings, items_per_page)

    page = request.GET.get('page')
    try:
        trackings = paginator.page(page)
    except PageNotAnInteger:
        trackings = paginator.page(1)
    except EmptyPage:
        trackings = paginator.page(paginator.num_pages)

    bar_chart_trackings = Tracking.objects.filter(created_by=request.user.id, document_id__isnull=False).values(
        'status').annotate(count=Count('id'))
    bar_chart = {tracking['status']: tracking['count'] for tracking in bar_chart_trackings}

    ten_days_ago = datetime.now() - timedelta(days=10)

    date_list = [ten_days_ago + timedelta(days=x) for x in range(11)]

    result = Document.objects.filter(created__gte=ten_days_ago, created_by=request.user.id) \
        .annotate(date=TruncDate('created')) \
        .values('date') \
        .annotate(count=Count('id')) \
        .order_by('date')

    count_by_date = {entry['date'].strftime('%Y-%m-%d'): entry['count'] for entry in result}

    linechart = [
        {'x': d.strftime('%Y-%m-%d'), 'y': count_by_date.get(d.strftime('%Y-%m-%d'), 0)}
        for d in date_list
    ]

    # return JsonResponse(list(linechart), safe=False)
    return render(request, 'home.html', {
        'trackings': trackings,
        'bar_chart': bar_chart if 'bar_chart' in locals() else {},
        'linechart': linechart
    })


@login_required(login_url='login')
def documents(request):
    query = request.GET.get('q')
    data = Document.objects.filter(Q(created_by__department=request.user.department)).all()
    if query:
        data = data.filter(Q(route_no__icontains=query))

    data = data.order_by('-id')

    items_per_page = 15
    paginator = Paginator(data, items_per_page)

    page = request.GET.get('page')
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    return render(request, 'documents.html', {'documents': data, 'query': query})


def createDocument(request):
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

            messages.success(request, {'response': 'Successfully saved document!'})

            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = DocumentForm()

    return render(request, 'create_documents.html', {'form': form})


def updateDocument(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    if request.method == 'POST':
        form = DocumentForm(request.POST, instance=document)
        if form.is_valid():
            document = form.save(commit=False)
            document.save()

            tracking = Tracking.objects.filter(document_id=document_id).first()
            if tracking:
                tracking.remarks = document.title
                tracking.save()

            messages.success(request, {'response': 'Successfully updated document!'})
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = DocumentForm(instance=document)

    return render(request, 'info_documents.html', {'form': form, 'document': document})


def deleteDocument(request):
    document_id = request.POST.get('document_id')
    try:
        document = Document.objects.get(pk=document_id)
        route_no = document.route_no
        document.delete()

        messages.error(request, {'response': f"Document with ROUTE NO: {route_no} has been deleted successfully."})
    except Document.DoesNotExist:
        messages.error(request, f"Document with id {document_id} does not exist.")
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")

    return redirect(request.META.get('HTTP_REFERER', '/'))


def trackDocument(request, pk):
    query = Q()
    if pk.isdigit():
        pk_value = int(pk)
        query |= Q(document_id=pk_value)
    else:
        pk_value = pk
        query |= Q(route_no=pk_value)

    tracking = Tracking.objects.filter(query, document_id__isnull=False).all()

    for track in tracking:
        track.duration = get_duration(track.created)

    return render(request, 'track_documents.html', {'tracking': tracking})


def releaseDocument(request, document_id):
    if request.method == 'POST':
        remarks = request.POST.get('remarks')
        released_to = Department.objects.get(pk=request.POST.get('released_to'))

        document = Document.objects.get(pk=document_id)
        document.status = "released"
        document.released_to = released_to
        document.save()

        Tracking.objects.create(
            route_no=document.route_no,
            status=document.status,
            document=document,
            created_by=request.user,
            released_to=released_to,
            remarks=remarks
        )

        messages.success(request, {
            'response': 'Successfully released document!',
            'data': {
                'status': document.status,
                'department': request.POST.get('released_to'),
                'route_no': document.route_no,
                'user_released': request.user.first_name + " " + request.user.last_name,
                'department_released': released_to.description,
                'remarks': remarks
            }
        }
                         )
        return redirect(request.META.get('HTTP_REFERER', '/'))

    departments = Department.objects.exclude(pk=request.user.department.id)
    return render(request, 'release_documents.html', {'document_id': document_id, 'departments': departments})


def incomingDocuments(request):
    query = request.GET.get('q')
    data = Document.objects.filter(
        Q(released_to=request.user.department, status='released') |
        Q(returned_to=request.user.department, status='returned')
    ).all()

    if query:
        data = data.filter(Q(route_no__icontains=query))

    data = data.order_by('-updated')

    items_per_page = 15
    paginator = Paginator(data, items_per_page)

    page = request.GET.get('page')
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    return render(request, 'incoming_documents.html', {'documents': data, 'query': query})


def acceptDocument(request):
    try:
        document_id = request.POST.get('document_id')
        remarks = request.POST.get('remarks')
        accepted_by = Department.objects.get(pk=request.user.department.id)

        document = Document.objects.get(pk=document_id)
        document.status = "accepted"
        document.released_to = None
        document.accepted_by = accepted_by
        document.save()

        Tracking.objects.create(
            route_no=document.route_no,
            status=document.status,
            document=document,
            created_by=request.user,
            accepted_by=accepted_by,
            remarks=remarks
        )
        messages.success(request, {
            'response': f"Document with ROUTE NO: {document.route_no} has been accepted successfully.",
            'data': {
                'status': document.status,
                'department': document.created_by.department.id,
                'route_no': document.route_no,
                'user_accepted_id': request.user.id,
                'user_accepted': request.user.first_name + " " + request.user.last_name,
                'department_accepted': request.user.department.description,
                'remarks': remarks
            }
        })
    except Document.DoesNotExist:
        messages.error(request, f"Document with id {document_id} does not exist.")
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        print(f"An error occurred: {e}")

    return redirect(request.META.get('HTTP_REFERER', '/'))


def cycleEndDocument(request):
    try:
        document_id = request.POST.get('document_id')
        remarks = request.POST.get('remarks')
        cycle_end_by = Department.objects.get(pk=request.user.department.id)

        document = Document.objects.get(pk=document_id)
        document.status = "cycled end"
        document.accepted_by = None
        document.cycle_end_by = cycle_end_by
        document.save()

        Tracking.objects.create(
            route_no=document.route_no,
            status=document.status,
            document=document,
            created_by=request.user,
            cycle_end_by=cycle_end_by,
            remarks=remarks
        )

        messages.success(request, {
            'response': f"The document with Route No: {document.route_no} has been cycled end successfully."})
    except Document.DoesNotExist:
        messages.error(request, f"Document with id {document_id} does not exist.")
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        print(f"An error occurred: {e}")

    return redirect(request.META.get('HTTP_REFERER', '/'))


def cycleEndDocs(request):
    query = request.GET.get('q')
    data = Document.objects.filter(cycle_end_by=request.user.department, status='cycled end').all()
    if query:
        data = data.filter(Q(route_no__icontains=query))

    data = data.order_by('-updated')

    items_per_page = 15
    paginator = Paginator(data, items_per_page)

    page = request.GET.get('page')
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    return render(request, 'cycle_end_documents.html', {'documents': data, 'query': query})


def outgoingDocuments(request):
    query = request.GET.get('q')
    data = Document.objects.filter(accepted_by=request.user.department, status='accepted').all()
    if query:
        data = data.filter(Q(route_no__icontains=query))

    data = data.order_by('-updated')

    items_per_page = 15
    paginator = Paginator(data, items_per_page)

    page = request.GET.get('page')
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    return render(request, 'outgoing_documents.html', {'documents': data, 'query': query})


def returnDocument(request):
    try:
        document_id = request.POST.get('document_id')
        remarks = request.POST.get('remarks')
        last_tracking = Tracking.objects.filter(document_id=document_id).order_by('-id').last()
        last_tracking = Tracking.objects.filter(document_id=document_id, id__gt=last_tracking.id).order_by('id').first()

        document = Document.objects.get(pk=document_id)
        document.status = "returned"
        document.accepted_by = None
        document.returned_to = last_tracking.created_by.department
        document.save()

        Tracking.objects.create(
            route_no=document.route_no,
            status=document.status,
            document=document,
            created_by=request.user,
            returned_to=document.returned_to,
            remarks=remarks
        )

        messages.success(request, {
            'response': f"The document with Route No: {document.route_no} has been returned successfully.",
            'data': {
                'status': document.status,
                'department': document.returned_to.id,
                'route_no': document.route_no,
                'user_returned': request.user.first_name + " " + request.user.last_name,
                'department_returned': document.created_by.department.description,
                'remarks': remarks
            }
        })

    except Document.DoesNotExist:
        messages.error(request, f"Document with id {document_id} does not exist.")
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        print(f"An error occurred: {e}")

    return redirect(request.META.get('HTTP_REFERER', '/'))


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
