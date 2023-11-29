from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('documents', views.documents, name="documents"),
    path('create_document', views.create_document, name="create_document"),
    path('update_document/<document_id>', views.update_document, name="update_document"),
    path('delete_document', views.delete_document, name="delete_document"),
    path('track_document/<pk>', views.track_document, name="track_document"),
]
