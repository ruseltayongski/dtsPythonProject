from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('documents', views.documents, name="documents"),
    path('create_document', views.createDocument, name="create_document"),
    path('update_document/<document_id>', views.updateDocument, name="update_document"),
    path('delete_document', views.deleteDocument, name="delete_document"),
    path('track_document/<pk>', views.trackDocument, name="track_document"),
    path('release_document/<document_id>', views.releaseDocument, name="release_document"),
    path('incoming_docs', views.incomingDocuments, name="incoming_docs"),
    path('accept_document', views.acceptDocument, name="accept_document"),
    path('outgoing_docs', views.outgoingDocuments, name="outgoing_docs"),
]
