from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DocumentForm


# Create your views here.

@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')


@login_required(login_url='login')
def documents(request):
    return render(request, 'documents.html', )


def create_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST)
        if form.is_valid():
            document = form.save(commit=False)

            document.created_by = request.user
            document.save()
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = DocumentForm()

    return render(request, 'create_documents.html', {'form': form})
