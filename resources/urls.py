from django.urls import path
from . import views
from .views import group_list, group_chat_view

urlpatterns = [
    path('upload/', views.upload_document, name='upload_document'),
    path('view/', views.view_documents, name='view_documents'),
    path('document/<int:document_id>/', views.serve_document, name='serve_document'),
    path('groups/create/', views.create_study_group, name='create_group'),
    path('groups/', views.group_list, name='group_list'),
    
    # NEW — detail page uses '/detail/'
    path('groups/<int:group_id>/detail/', views.group_detail, name='group_detail'),

    # Chat page
    path('groups/<int:group_id>/chat/', views.group_chat_view, name='group_chat'),
    
    # AJAX endpoint for sending messages
    path('groups/<int:group_id>/send/', views.send_message, name='send_message'),

    path('groups/<int:group_id>/join/', views.join_group, name='join_group'),

    path('delete-message/<int:message_id>/', views.delete_message, name='delete_message'),

    path('chat/token/', views.get_chat_token, name='get_chat_token'),

    # ============ GROUP MANAGEMENT URLS ============
    # Edit, delete, leave group
    path('groups/<int:group_id>/edit/', views.edit_group, name='edit_group'),
    path('groups/<int:group_id>/delete/', views.delete_group, name='delete_group'),
    path('groups/<int:group_id>/leave/', views.leave_group, name='leave_group'),
    
    # Permissions and member management
    path('groups/<int:group_id>/permissions/', views.manage_permissions, name='manage_permissions'),
    path('groups/<int:group_id>/remove/<int:user_id>/', views.remove_member, name='remove_member'),
    
    # Invite system
    path('groups/<int:group_id>/invites/', views.group_invites, name='group_invites'),
    path('groups/<int:group_id>/invites/create/', views.create_invite_link, name='create_invite_link'),
    path('invites/<int:invite_id>/deactivate/', views.deactivate_invite, name='deactivate_invite'),
    path('invite/<uuid:invite_token>/', views.join_via_invite_link, name='join_via_invite_link'),
    path('join-code/', views.join_via_code, name='join_via_code'),
    
    # ============ FRIENDS URLS ============
    path('friends/', views.friends_list, name='friends_list'),
    path('friends/add/', views.add_friend, name='add_friend'),
    path('friends/add-from-group/<int:user_id>/', views.add_friend_from_group, name='add_friend_from_group'),
    path('friends/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friends/decline/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('friends/remove/<int:user_id>/', views.remove_friend, name='remove_friend'),
    
    # ============ PRIVATE MESSAGING URLS ============
    path('chats/', views.private_chats_list, name='private_chats_list'),
    path('chats/<int:chat_id>/', views.private_chat_view, name='private_chat'),
    path('chats/start/<int:user_id>/', views.start_private_chat, name='start_private_chat'),
    path('chats/<int:chat_id>/send/', views.send_private_message, name='send_private_message'),
    
    # ============ REACTIONS & ATTACHMENTS ============
    path('reactions/add/', views.add_reaction, name='add_reaction'),
    path('attachments/upload/', views.upload_message_attachment, name='upload_message_attachment'),
]
