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
from django.db import connection
import json


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

    bar_chart = get_bar_chart_data(request.user.id)
    line_chart = get_line_chart_data(request.user.id)

    # return JsonResponse(line_chart, safe=False)
    return render(request, 'home.html', {
        'trackings': trackings,
        'bar_chart': bar_chart if 'bar_chart' in locals() else {},
        'linechart': line_chart
    })


def get_bar_chart_data(user_id):
    with connection.cursor() as cursor:
        # Call the stored procedure
        cursor.callproc('GetBarChartData', [user_id])
        results = cursor.fetchall()
        bar_chart = {status: count for status, count in results}

    return bar_chart


def get_line_chart_data(user_id):
    with connection.cursor() as cursor:
        # Call the stored procedure
        cursor.callproc('GetLineChartData', [user_id])
        results = cursor.fetchall()
        line_chart = [{'x': date.strftime('%Y-%m-%d'), 'y': count} for date, count in results]

    return line_chart


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
            title = request.POST.get('title')
            content = request.POST.get('content')
            user_id = request.user.id
            response = save_document_procedure(title, content, user_id)
            messages.success(request, {'response': response})

            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = DocumentForm()

    return render(request, 'create_documents.html', {'form': form})


def save_document_procedure(title, user_id, content):
    with connection.cursor() as cursor:
        # Call the stored procedure
        cursor.callproc('SaveDocument', [title, user_id, content])

        # Fetch the result
        result = cursor.fetchone()

    # Extract the string value from the tuple
    response_message = result[0] if result else None

    return response_message


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
    tracking = call_track_document(pk)
    #return JsonResponse(call_track_document(pk), safe=False)
    return render(request, 'track_documents.html', {'tracking': tracking})


def call_track_document(pk_value):
    with connection.cursor() as cursor:
        # Call the stored procedure
        cursor.callproc('trackDocument', [pk_value])

        # Fetch the result set from the OUT parameter cursor
        result_set = cursor.fetchall()

        # Fetch column names from the cursor description
        column_names = [desc[0] for desc in cursor.description]

        # Create a list of dictionaries with column names and values
        result_list = [dict(zip(column_names, row)) for row in result_set]

        return result_list


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
    document_id = request.POST.get('document_id')
    remarks = request.POST.get('remarks')
    accept_document_procedure(document_id, remarks, request.user.id)
    document = Document.objects.get(pk=document_id)
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

    return redirect(request.META.get('HTTP_REFERER', '/'))

    # try:
    #     document_id = request.POST.get('document_id')
    #     remarks = request.POST.get('remarks')
    #     accepted_by = Department.objects.get(pk=request.user.department.id)
    #
    #     document = Document.objects.get(pk=document_id)
    #     document.status = "accepted"
    #     document.released_to = None
    #     document.accepted_by = accepted_by
    #     document.save()
    #
    #     Tracking.objects.create(
    #         route_no=document.route_no,
    #         status=document.status,
    #         document=document,
    #         created_by=request.user,
    #         accepted_by=accepted_by,
    #         remarks=remarks
    #     )
    #     messages.success(request, {
    #         'response': f"Document with ROUTE NO: {document.route_no} has been accepted successfully.",
    #         'data': {
    #             'status': document.status,
    #             'department': document.created_by.department.id,
    #             'route_no': document.route_no,
    #             'user_accepted_id': request.user.id,
    #             'user_accepted': request.user.first_name + " " + request.user.last_name,
    #             'department_accepted': request.user.department.description,
    #             'remarks': remarks
    #         }
    #     })
    # except Document.DoesNotExist:
    #     messages.error(request, f"Document with id {document_id} does not exist.")
    # except Exception as e:
    #     messages.error(request, f"An error occurred: {e}")
    #     print(f"An error occurred: {e}")

    #return redirect(request.META.get('HTTP_REFERER', '/'))


def accept_document_procedure(document_id, remarks, user_id):
    with connection.cursor() as cursor:
        # Call the stored procedure
        cursor.callproc('AcceptDocuments', [document_id, remarks, user_id])

        # If your stored procedure returns any result, you can fetch it using fetchall()
        result = cursor.fetchall()

        # Commit the transaction
        connection.commit()

        return result  # Return the result if needed



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
