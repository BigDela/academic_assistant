from django.shortcuts import render, redirect, get_object_or_404
from .models import Document, Course, StudyGroup, Message, GroupInvite, Friendship, PrivateChat, PrivateMessage, MessageReaction, MessageAttachment
from django.contrib.auth.decorators import login_required
from .forms import StudyGroupForm, MessageForm, DocumentUploadForm, EditGroupForm, ManagePermissionsForm, CreateInviteForm, JoinGroupCodeForm, AddFriendForm, PrivateMessageForm, MessageAttachmentForm
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()



@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            form.save_m2m()
            messages.success(request, "Document uploaded successfully!")
            return redirect('view_documents')
    else:
        form = DocumentUploadForm(user=request.user)

    return render(request, 'resources/upload.html', {'form': form})

@login_required
def serve_document(request, document_id):
    """Serve document with membership verification"""
    document = get_object_or_404(Document, id=document_id)
    
    # If document belongs to a group, verify membership
    if document.group:
        if request.user not in document.group.members.all():
            messages.error(request, "You don't have access to this document. Join the group first.")
            return redirect('group_detail', group_id=document.group.id)
    
    # Use X-Accel-Redirect for production or redirect to file URL for development
    from django.http import FileResponse
    import os
    
    if os.path.exists(document.file.path):
        response = FileResponse(document.file.open('rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(document.file.name)}"'
        return response
    else:
        messages.error(request, "Document file not found.")
        return redirect('view_documents')

def view_documents(request):
    course_id = request.GET.get('course')
    courses = Course.objects.all()
    
    # Filter documents: public documents (no group) OR user is member of the group
    if request.user.is_authenticated:
        user_groups = request.user.study_groups.all()
        documents = Document.objects.filter(
            Q(group__isnull=True) | Q(group__in=user_groups)
        )
    else:
        # Only show documents without a group for anonymous users
        documents = Document.objects.filter(group__isnull=True)
    
    if course_id:
        documents = documents.filter(course__id=course_id)
    return render(request, 'resources/view.html', {'documents': documents, 'courses': courses})



@login_required
def create_study_group(request):
    if request.method == 'POST':
        form = StudyGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            group.members.add(request.user)
            messages.success(request, "Study group created successfully!")
            return redirect('group_list')
    else:
        form = StudyGroupForm()
    return render(request, 'resources/create_group.html', {'form': form})

@login_required
def group_list(request):
    groups = StudyGroup.objects.all()
    return render(request, 'resources/group_list.html', {'groups': groups})
@login_required
def group_detail(request, group_id):
    group = get_object_or_404(StudyGroup, id=group_id)
    
    # Check if user is a member to view group documents
    is_member = request.user in group.members.all()

    if request.method == 'POST':
        if not is_member:
            messages.error(request, "You must be a member to post messages.")
            return redirect('group_detail', group_id=group.id)
            
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.group = group
            message.user = request.user
            message.save()
            return redirect('group_detail', group_id=group.id)
    else:
        form = MessageForm()

    messages_list = group.messages.all()

    return render(request, 'resources/group_detail.html', {
        'group': group,
        'messages': messages_list,
        'form': form,
        'is_member': is_member
    })
@login_required
def join_group(request, group_id):
    group = get_object_or_404(StudyGroup, id=group_id)
    if request.user not in group.members.all():
        group.members.add(request.user)
        messages.success(request, "You joined the group!")
    else:
        messages.info(request, "You are already a member of this group.")
    return redirect('group_detail', group_id=group.id)


import pusher

pusher_client = pusher.Pusher(
    app_id=settings.PUSHER_APP_ID,
    key=settings.PUSHER_KEY,
    secret=settings.PUSHER_SECRET,
    cluster=settings.PUSHER_CLUSTER,
    ssl=True
)

@login_required
def group_chat_view(request, group_id):
    """Render the chat page with existing messages."""
    group = get_object_or_404(StudyGroup, id=group_id)
    
    # Verify user is a member of the group
    if request.user not in group.members.all():
        messages.error(request, "You must be a member of this group to access the chat.")
        return redirect('group_detail', group_id=group.id)
    
    messages_qs = group.messages.all().order_by('timestamp')
    documents = group.documents.all()

    return render(request, 'resources/group_chat.html', {
        'group': group,
        'messages': messages_qs,
        'documents': documents,
        'pusher_key': settings.PUSHER_KEY,
        'pusher_cluster': settings.PUSHER_CLUSTER,
    })


@login_required
@require_POST
def send_message(request, group_id):
    """Handle AJAX message sending and trigger Pusher event."""
    group = get_object_or_404(StudyGroup, id=group_id)
    
    # Verify user is a member
    if request.user not in group.members.all():
        return JsonResponse({'success': False, 'error': 'You are not a member of this group'}, status=403)
    
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'success': False, 'error': 'Message content cannot be empty'}, status=400)
    
    if len(content) > 5000:
        return JsonResponse({'success': False, 'error': 'Message too long (max 5000 characters)'}, status=400)
    
    # Create and save message
    from .models import Message
    message = Message.objects.create(
        group=group,
        user=request.user,
        content=content
    )
    
    # Trigger Pusher event for real-time updates to other users
    pusher_client.trigger(f'group-{group.id}', 'new-message', {
        'username': request.user.username,
        'message': message.content,
        'timestamp': message.timestamp.isoformat(),
        'message_id': message.id,
    })
    
    return JsonResponse({
        'success': True,
        'message_id': message.id,
        'timestamp': message.timestamp.isoformat(),
    })


# ============ GROUP MANAGEMENT VIEWS ============

@login_required
def edit_group(request, group_id):
    """Edit group information (creator and editors only)"""
    group = get_object_or_404(StudyGroup, id=group_id)
    
    # Check permission
    if not group.can_edit_group(request.user):
        messages.error(request, "You don't have permission to edit this group.")
        return redirect('group_detail', group_id=group.id)
    
    if request.method == 'POST':
        form = EditGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Group updated successfully!")
            return redirect('group_detail', group_id=group.id)
    else:
        form = EditGroupForm(instance=group)
    
    return render(request, 'resources/edit_group.html', {
        'form': form,
        'group': group
    })


@login_required
def delete_group(request, group_id):
    """Delete a study group (creator only)"""
    group = get_object_or_404(StudyGroup, id=group_id)
    
    # Only creator can delete
    if request.user != group.creator:
        messages.error(request, "Only the group creator can delete this group.")
        return redirect('group_detail', group_id=group.id)
    
    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f"Group '{group_name}' has been deleted.")
        return redirect('group_list')
    
    return render(request, 'resources/delete_group.html', {'group': group})


@login_required
def leave_group(request, group_id):
    """Leave a study group"""
    group = get_object_or_404(StudyGroup, id=group_id)
    
    # Creator cannot leave their own group
    if request.user == group.creator:
        messages.error(request, "Group creators cannot leave. Please delete the group or transfer ownership.")
        return redirect('group_detail', group_id=group.id)
    
    if request.user not in group.members.all():
        messages.info(request, "You are not a member of this group.")
        return redirect('group_list')
    
    if request.method == 'POST':
        # Remove from members, admins, and editors
        group.members.remove(request.user)
        group.admins.remove(request.user)
        group.editors.remove(request.user)
        messages.success(request, f"You have left '{group.name}'.")
        return redirect('group_list')
    
    return render(request, 'resources/leave_group.html', {'group': group})


@login_required
def manage_permissions(request, group_id):
    """Manage admin and editor permissions (creator and admins only)"""
    group = get_object_or_404(StudyGroup, id=group_id)
    
    # Check permission
    if not group.can_manage_members(request.user):
        messages.error(request, "You don't have permission to manage permissions.")
        return redirect('group_detail', group_id=group.id)
    
    if request.method == 'POST':
        form = ManagePermissionsForm(request.POST, group=group)
        if form.is_valid():
            # Clear and set new permissions
            group.admins.set(form.cleaned_data['admins'])
            group.editors.set(form.cleaned_data['editors'])
            messages.success(request, "Permissions updated successfully!")
            return redirect('group_detail', group_id=group.id)
    else:
        # Pre-populate with current permissions
        form = ManagePermissionsForm(
            group=group,
            initial={
                'admins': group.admins.all(),
                'editors': group.editors.all()
            }
        )
    
    return render(request, 'resources/manage_permissions.html', {
        'form': form,
        'group': group
    })


@login_required
def remove_member(request, group_id, user_id):
    """Remove a member from the group (admins only)"""
    group = get_object_or_404(StudyGroup, id=group_id)
    
    # Check permission
    if not group.can_manage_members(request.user):
        messages.error(request, "You don't have permission to remove members.")
        return redirect('group_detail', group_id=group.id)
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    member = get_object_or_404(User, id=user_id)
    
    # Cannot remove creator
    if member == group.creator:
        messages.error(request, "Cannot remove the group creator.")
        return redirect('group_detail', group_id=group.id)
    
    if member not in group.members.all():
        messages.info(request, "User is not a member of this group.")
        return redirect('group_detail', group_id=group.id)
    
    if request.method == 'POST':
        group.members.remove(member)
        group.admins.remove(member)
        group.editors.remove(member)
        messages.success(request, f"{member.username} has been removed from the group.")
        return redirect('group_detail', group_id=group.id)
    
    return render(request, 'resources/remove_member.html', {
        'group': group,
        'member': member
    })


@login_required
def create_invite_link(request, group_id):
    """Create a custom invite link (admins only)"""
    group = get_object_or_404(StudyGroup, id=group_id)
    
    if not group.can_manage_members(request.user):
        messages.error(request, "You don't have permission to create invite links.")
        return redirect('group_detail', group_id=group.id)
    
    if request.method == 'POST':
        form = CreateInviteForm(request.POST)
        if form.is_valid():
            invite = form.save(commit=False)
            invite.group = group
            invite.created_by = request.user
            invite.save()
            messages.success(request, "Invite link created successfully!")
            return redirect('group_invites', group_id=group.id)
    else:
        form = CreateInviteForm()
    
    return render(request, 'resources/create_invite.html', {
        'form': form,
        'group': group
    })


@login_required
def group_invites(request, group_id):
    """View all invite links for a group (admins only)"""
    group = get_object_or_404(StudyGroup, id=group_id)
    
    if not group.can_manage_members(request.user):
        messages.error(request, "You don't have permission to view invite links.")
        return redirect('group_detail', group_id=group.id)
    
    invites = group.invites.all().order_by('-created_at')
    
    return render(request, 'resources/group_invites.html', {
        'group': group,
        'invites': invites
    })


@login_required
def deactivate_invite(request, invite_id):
    """Deactivate an invite link"""
    invite = get_object_or_404(GroupInvite, id=invite_id)
    group = invite.group
    
    if not group.can_manage_members(request.user):
        messages.error(request, "You don't have permission to deactivate invite links.")
        return redirect('group_detail', group_id=group.id)
    
    invite.is_active = False
    invite.save()
    messages.success(request, "Invite link deactivated.")
    return redirect('group_invites', group_id=group.id)


@login_required
def join_via_invite_link(request, invite_token):
    """Join group via invite link"""
    invite = get_object_or_404(GroupInvite, invite_token=invite_token)
    group = invite.group
    
    if not invite.can_be_used():
        messages.error(request, "This invite link is no longer valid.")
        return redirect('group_list')
    
    if request.user in group.members.all():
        messages.info(request, "You are already a member of this group.")
        return redirect('group_detail', group_id=group.id)
    
    # Add user to group and increment invite usage
    group.members.add(request.user)
    invite.use_invite()
    messages.success(request, f"You have joined '{group.name}'!")
    return redirect('group_detail', group_id=group.id)


@login_required
def join_via_code(request):
    """Join group using invite code"""
    if request.method == 'POST':
        form = JoinGroupCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['invite_code']
            try:
                group = StudyGroup.objects.get(invite_code=code)
                
                if not group.is_invite_active:
                    messages.error(request, "This group is not accepting new members via invite code.")
                    return redirect('group_list')
                
                if request.user in group.members.all():
                    messages.info(request, "You are already a member of this group.")
                    return redirect('group_detail', group_id=group.id)
                
                group.members.add(request.user)
                messages.success(request, f"You have joined '{group.name}'!")
                return redirect('group_detail', group_id=group.id)
                
            except StudyGroup.DoesNotExist:
                messages.error(request, "Invalid invite code.")
    else:
        form = JoinGroupCodeForm()
    
    return render(request, 'resources/join_via_code.html', {'form': form})


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@login_required
@require_POST
@csrf_exempt
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, user=request.user)

    group_id = message.group.id
    message.delete()

    # Notify via Pusher
    pusher_client.trigger(f'group-{group_id}', 'delete-message', {
        'message_id': message_id
    })

    return JsonResponse({'status': 'success'})


from django.http import JsonResponse
from stream_chat import StreamChat
from django.conf import settings
from django.contrib.auth.decorators import login_required

@login_required
def get_chat_token(request):
    client = StreamChat(api_key=settings.STREAM_API_KEY, api_secret=settings.STREAM_API_SECRET)
    user_id = str(request.user.id)
    client.upsert_user({"id": user_id, "name": request.user.username})
    token = client.create_token(user_id)
    return JsonResponse({"token": token, "user_id": user_id, "api_key": settings.STREAM_API_KEY})


# ============ FRIEND MANAGEMENT VIEWS ============

@login_required
def friends_list(request):
    """View all friends and friend requests"""
    friends = Friendship.get_friends(request.user)
    
    # Pending requests sent by user
    sent_requests = Friendship.objects.filter(from_user=request.user, status='pending')
    
    # Pending requests received by user
    received_requests = Friendship.objects.filter(to_user=request.user, status='pending')
    
    # Get study group members who aren't friends yet
    group_members = User.objects.filter(
        study_groups__in=request.user.study_groups.all()
    ).exclude(id=request.user.id).distinct()
    
    # Filter out existing friends
    friend_ids = [f.id for f in friends]
    potential_friends = group_members.exclude(id__in=friend_ids)
    
    return render(request, 'resources/friends_list.html', {
        'friends': friends,
        'sent_requests': sent_requests,
        'received_requests': received_requests,
        'potential_friends': potential_friends[:10],  # Limit to 10 suggestions
    })


@login_required
def add_friend(request):
    """Send friend request"""
    if request.method == 'POST':
        form = AddFriendForm(request.POST, current_user=request.user)
        if form.is_valid():
            username = form.cleaned_data['username']
            to_user = User.objects.get(username=username)
            
            Friendship.objects.create(
                from_user=request.user,
                to_user=to_user,
                status='pending'
            )
            
            messages.success(request, f"Friend request sent to {username}!")
            return redirect('friends_list')
    else:
        form = AddFriendForm(current_user=request.user)
    
    return render(request, 'resources/add_friend.html', {'form': form})


@login_required
def add_friend_from_group(request, user_id):
    """Add friend directly from study group"""
    to_user = get_object_or_404(User, id=user_id)
    
    if to_user == request.user:
        messages.error(request, "You cannot add yourself as a friend.")
        return redirect('friends_list')
    
    # Check if already friends or request pending
    existing = Friendship.objects.filter(
        Q(from_user=request.user, to_user=to_user) |
        Q(from_user=to_user, to_user=request.user)
    ).first()
    
    if existing:
        if existing.status == 'accepted':
            messages.info(request, "You are already friends with this user.")
        elif existing.status == 'pending':
            messages.info(request, "Friend request is already pending.")
    else:
        Friendship.objects.create(
            from_user=request.user,
            to_user=to_user,
            status='pending'
        )
        messages.success(request, f"Friend request sent to {to_user.username}!")
    
    return redirect('friends_list')


@login_required
def accept_friend_request(request, request_id):
    """Accept a friend request"""
    friendship = get_object_or_404(Friendship, id=request_id, to_user=request.user, status='pending')
    friendship.status = 'accepted'
    friendship.save()
    
    messages.success(request, f"You are now friends with {friendship.from_user.username}!")
    return redirect('friends_list')


@login_required
def decline_friend_request(request, request_id):
    """Decline a friend request"""
    friendship = get_object_or_404(Friendship, id=request_id, to_user=request.user, status='pending')
    friendship.status = 'declined'
    friendship.save()
    
    messages.info(request, "Friend request declined.")
    return redirect('friends_list')


@login_required
def remove_friend(request, user_id):
    """Remove a friend"""
    other_user = get_object_or_404(User, id=user_id)
    
    friendship = Friendship.objects.filter(
        Q(from_user=request.user, to_user=other_user, status='accepted') |
        Q(from_user=other_user, to_user=request.user, status='accepted')
    ).first()
    
    if friendship:
        friendship.delete()
        messages.success(request, f"You are no longer friends with {other_user.username}.")
    
    return redirect('friends_list')


# ============ PRIVATE MESSAGING VIEWS ============

@login_required
def private_chats_list(request):
    """View all private chats"""
    chats = PrivateChat.objects.filter(
        Q(participant1=request.user) | Q(participant2=request.user)
    ).select_related('participant1', 'participant2')
    
    # Add last message and unread count to each chat
    chat_data = []
    for chat in chats:
        last_message = chat.messages.order_by('-timestamp').first()
        unread_count = chat.messages.filter(
            is_read=False
        ).exclude(sender=request.user).count()
        
        chat_data.append({
            'chat': chat,
            'other_user': chat.get_other_participant(request.user),
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    return render(request, 'resources/private_chats_list.html', {'chat_data': chat_data})


@login_required
def private_chat_view(request, chat_id):
    """View and send messages in a private chat"""
    chat = get_object_or_404(PrivateChat, id=chat_id)
    
    # Verify user is participant
    if request.user not in [chat.participant1, chat.participant2]:
        messages.error(request, "You don't have access to this chat.")
        return redirect('private_chats_list')
    
    other_user = chat.get_other_participant(request.user)
    
    # Mark messages as read
    chat.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    # Get all messages (including replies) with parent_message data
    messages_qs = chat.messages.select_related('parent_message', 'parent_message__sender', 'sender').order_by('timestamp')
    
    # Get reaction emoji choices for the template
    from .models import MessageReaction
    reaction_emojis = MessageReaction.EMOJI_CHOICES
    
    return render(request, 'resources/private_chat.html', {
        'chat': chat,
        'other_user': other_user,
        'messages': messages_qs,
        'reaction_emojis': reaction_emojis,
        'pusher_key': settings.PUSHER_KEY,
        'pusher_cluster': settings.PUSHER_CLUSTER,
    })


@login_required
def start_private_chat(request, user_id):
    """Start or continue a private chat with another user"""
    other_user = get_object_or_404(User, id=user_id)
    
    if other_user == request.user:
        messages.error(request, "You cannot chat with yourself.")
        return redirect('private_chats_list')
    
    # Check if users are friends
    if not Friendship.are_friends(request.user, other_user):
        messages.error(request, "You must be friends to start a private chat.")
        return redirect('friends_list')
    
    chat = PrivateChat.get_or_create_chat(request.user, other_user)
    return redirect('private_chat', chat_id=chat.id)


@login_required
@require_POST
def send_private_message(request, chat_id):
    """AJAX endpoint for sending private messages"""
    chat = get_object_or_404(PrivateChat, id=chat_id)
    
    # Verify user is participant
    if request.user not in [chat.participant1, chat.participant2]:
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
    
    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id')
    
    if not content:
        return JsonResponse({'success': False, 'error': 'Message cannot be empty'}, status=400)
    
    # Create message
    message = PrivateMessage.objects.create(
        chat=chat,
        sender=request.user,
        content=content,
        parent_message_id=parent_id if parent_id else None
    )
    
    # Update chat timestamp
    chat.save()  # This triggers auto_now on updated_at
    
    # Trigger Pusher event
    pusher_client.trigger(f'private-chat-{chat.id}', 'new-message', {
        'message_id': message.id,
        'sender': request.user.username,
        'content': message.content,
        'timestamp': message.timestamp.isoformat(),
        'parent_id': parent_id
    })
    
    return JsonResponse({
        'success': True,
        'message_id': message.id,
        'timestamp': message.timestamp.isoformat()
    })


# ============ MESSAGE REACTIONS & ATTACHMENTS ============

@login_required
@require_POST
def add_reaction(request):
    """Add emoji reaction to a message"""
    emoji = request.POST.get('emoji')
    message_type = request.POST.get('message_type')  # 'group' or 'private'
    message_id = request.POST.get('message_id')
    
    if not all([emoji, message_type, message_id]):
        return JsonResponse({'success': False, 'error': 'Missing parameters'}, status=400)
    
    try:
        if message_type == 'group':
            message = get_object_or_404(Message, id=message_id)
            # Check if user is group member
            if request.user not in message.group.members.all():
                return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
            
            # Toggle reaction
            reaction, created = MessageReaction.objects.get_or_create(
                user=request.user,
                group_message=message,
                emoji=emoji
            )
            
            if not created:
                reaction.delete()
                action = 'removed'
            else:
                action = 'added'
            
            # Trigger Pusher
            pusher_client.trigger(f'group-{message.group.id}', 'reaction-update', {
                'message_id': message_id,
                'emoji': emoji,
                'user': request.user.username,
                'action': action
            })
            
        else:  # private
            message = get_object_or_404(PrivateMessage, id=message_id)
            # Check if user is participant
            if request.user not in [message.chat.participant1, message.chat.participant2]:
                return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
            
            # Toggle reaction
            reaction, created = MessageReaction.objects.get_or_create(
                user=request.user,
                private_message=message,
                emoji=emoji
            )
            
            if not created:
                reaction.delete()
                action = 'removed'
            else:
                action = 'added'
            
            # Trigger Pusher
            pusher_client.trigger(f'private-chat-{message.chat.id}', 'reaction-update', {
                'message_id': message_id,
                'emoji': emoji,
                'user': request.user.username,
                'action': action
            })
        
        return JsonResponse({'success': True, 'action': action})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def upload_message_attachment(request):
    """Upload file attachment for a message"""
    chat_type = request.POST.get('chat_type')  # 'group' or 'private'
    chat_id = request.POST.get('chat_id')
    
    form = MessageAttachmentForm(request.POST, request.FILES)
    
    if form.is_valid():
        attachment = form.save(commit=False)
        attachment.filename = form.cleaned_data['filename']
        attachment.file_size = form.cleaned_data['file_size']
        attachment.file_type = form.cleaned_data['file_type']
        
        # For now, save without linking to message
        # In actual implementation, this would be called with message creation
        attachment.save()
        
        return JsonResponse({
            'success': True,
            'attachment_id': attachment.id,
            'filename': attachment.filename,
            'file_size': attachment.get_file_size_display(),
            'file_url': attachment.file.url
        })
    
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)
