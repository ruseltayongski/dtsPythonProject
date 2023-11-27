from django.shortcuts import render, redirect
from .models import Employee
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


# Create your views here.


def loginPage(request):
    username = ''
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            Employee.objects.get(username=username)
        except:
            messages.error(request, 'These usernames do not exist')

        employee = authenticate(request, username=username, password=password)

        if employee is not None:
            login(request, employee)
            return redirect('/')
        else:
            messages.error(request, 'These credentials do not match our records')

    context = {
        'username': username
    }
    return render(request, 'loginPage.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')
