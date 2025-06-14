from django.urls import path
from . import views
from .views import group_list, group_chat_view

urlpatterns = [
    path('upload/', views.upload_document, name='upload_document'),
    path('view/', views.view_documents, name='view_documents'),
    path('groups/create/', views.create_study_group, name='create_group'),
    path('groups/', views.group_list, name='group_list'),
    
    # NEW — detail page uses '/detail/'
    path('groups/<int:group_id>/detail/', views.group_detail, name='group_detail'),

    # Chat page
    path('groups/<int:group_id>/chat/', views.group_chat_view, name='group_chat'),

    path('groups/<int:group_id>/join/', views.join_group, name='join_group'),

    path('delete-message/<int:message_id>/', views.delete_message, name='delete_message'),

    path('chat/token/', views.get_chat_token, name='get_chat_token'),

    
]
