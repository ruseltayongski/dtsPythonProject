from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('documents', views.documents, name="documents"),
    path('create_document', views.create_document, name="create_document"),
]
