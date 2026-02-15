"""
Dashboard views for the home page and notification system.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Max, Subquery, OuterRef, Exists
from django.utils import timezone
from datetime import timedelta

from .models import (
    Document, StudyGroup, Message, Friendship, PrivateChat,
    PrivateMessage, GroupJoinRequest, Notification
)


def home(request):
    """Dashboard home view with activity feed, stats, and quick access."""
    if not request.user.is_authenticated:
        return render(request, 'home.html')

    user = request.user

    # ── Stats ──────────────────────────────────────────────────
    user_groups = StudyGroup.objects.filter(members=user)
    documents_uploaded = Document.objects.filter(uploaded_by=user).count()
    friends_count = Friendship.objects.filter(
        Q(from_user=user, status='accepted') | Q(to_user=user, status='accepted')
    ).count()
    private_chats_count = PrivateChat.objects.filter(
        Q(participant1=user) | Q(participant2=user)
    ).count()
    pending_join_requests = GroupJoinRequest.objects.filter(
        group__in=user_groups.filter(Q(creator=user) | Q(admins=user)),
        status='pending'
    ).distinct().count()
    pending_friend_requests = Friendship.objects.filter(
        to_user=user, status='pending'
    ).count()

    # ── My Study Groups (with unread message indicators) ──────
    # Get user's groups with the latest message timestamp
    my_groups = user_groups.annotate(
        latest_message_time=Max('messages__timestamp'),
        member_count=Count('members', distinct=True),
        message_count=Count('messages', distinct=True),
    ).order_by('-latest_message_time')[:6]

    # ── Recent Documents ──────────────────────────────────────
    # Documents uploaded by user or shared in their groups
    recent_documents = Document.objects.filter(
        Q(uploaded_by=user) | Q(group__in=user_groups)
    ).select_related('uploaded_by').order_by('-uploaded_at')[:5]

    # ── Activity Feed ─────────────────────────────────────────
    # Collect recent activities from multiple sources
    activities = []

    # Recent group messages (last 5 across all groups)
    recent_group_msgs = Message.objects.filter(
        group__in=user_groups
    ).exclude(
        user=user
    ).select_related('user', 'group').order_by('-timestamp')[:5]

    for msg in recent_group_msgs:
        display_name = msg.user.get_full_name() or msg.user.username
        activities.append({
            'type': 'group_message',
            'icon': 'message',
            'color': '#4A90E2',
            'title': f'{display_name} in {msg.group.name}',
            'preview': msg.content[:80] + ('...' if len(msg.content) > 80 else ''),
            'timestamp': msg.timestamp,
            'url': f'/resources/groups/{msg.group.id}/chat/',
            'avatar_user': msg.user,
        })

    # Recent private messages
    user_chats = PrivateChat.objects.filter(
        Q(participant1=user) | Q(participant2=user)
    )
    recent_private_msgs = PrivateMessage.objects.filter(
        chat__in=user_chats
    ).exclude(
        sender=user
    ).select_related('sender', 'chat', 'chat__participant1', 'chat__participant2').order_by('-timestamp')[:5]

    for msg in recent_private_msgs:
        display_name = msg.sender.get_full_name() or msg.sender.username
        activities.append({
            'type': 'private_message',
            'icon': 'mail',
            'color': '#10B981',
            'title': f'{display_name} sent you a message',
            'preview': msg.content[:80] + ('...' if len(msg.content) > 80 else ''),
            'timestamp': msg.timestamp,
            'url': f'/resources/chats/{msg.chat.id}/',
            'avatar_user': msg.sender,
        })

    # Recent friend request events
    recent_friend_events = Friendship.objects.filter(
        Q(to_user=user, status='pending') |
        Q(from_user=user, status='accepted', updated_at__gte=timezone.now() - timedelta(days=7))
    ).select_related('from_user', 'to_user').order_by('-updated_at')[:3]

    for fr in recent_friend_events:
        if fr.status == 'pending' and fr.to_user == user:
            activities.append({
                'type': 'friend_request',
                'icon': 'user',
                'color': '#F59E0B',
                'title': f'{fr.from_user.get_full_name() or fr.from_user.username} sent a friend request',
                'preview': 'Tap to accept or decline',
                'timestamp': fr.created_at,
                'url': '/resources/friends/',
                'avatar_user': fr.from_user,
            })
        elif fr.status == 'accepted' and fr.from_user == user:
            activities.append({
                'type': 'friend_accepted',
                'icon': 'check',
                'color': '#10B981',
                'title': f'{fr.to_user.get_full_name() or fr.to_user.username} accepted your friend request',
                'preview': 'You are now friends!',
                'timestamp': fr.updated_at,
                'url': '/resources/friends/',
                'avatar_user': fr.to_user,
            })

    # Recent group join requests (for group admins)
    admin_groups = user_groups.filter(Q(creator=user) | Q(admins=user))
    recent_join_requests = GroupJoinRequest.objects.filter(
        group__in=admin_groups,
        status='pending'
    ).select_related('user', 'group').order_by('-created_at')[:3]

    for jr in recent_join_requests:
        activities.append({
            'type': 'group_join_request',
            'icon': 'users',
            'color': '#8B5CF6',
            'title': f'{jr.user.get_full_name() or jr.user.username} wants to join {jr.group.name}',
            'preview': jr.message[:60] if jr.message else 'Pending your approval',
            'timestamp': jr.created_at,
            'url': '/resources/discover/join-requests/',
            'avatar_user': jr.user,
        })

    # Sort all activities by timestamp, take latest 8
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    activities = activities[:8]

    # ── Unread Counts ─────────────────────────────────────────
    unread_notifications = Notification.objects.filter(
        recipient=user, is_read=False
    ).count()

    # Unread private messages count
    unread_private_msgs = PrivateMessage.objects.filter(
        chat__in=user_chats,
        is_read=False,
    ).exclude(sender=user).count()

    context = {
        # Stats
        'groups_count': user_groups.count(),
        'documents_uploaded': documents_uploaded,
        'friends_count': friends_count,
        'private_chats_count': private_chats_count,
        'pending_join_requests': pending_join_requests,
        'pending_friend_requests': pending_friend_requests,
        # Groups
        'my_groups': my_groups,
        # Documents
        'recent_documents': recent_documents,
        # Activity Feed
        'activities': activities,
        # Notifications
        'unread_notifications': unread_notifications,
        'unread_private_msgs': unread_private_msgs,
    }

    return render(request, 'home.html', context)


@login_required
def notifications_list(request):
    """View all notifications"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('from_user', 'group', 'private_chat').order_by('-created_at')[:50]

    return render(request, 'notifications.html', {
        'notifications': notifications,
    })


@login_required
@require_POST
def mark_notifications_read(request):
    """Mark specific notifications as read (AJAX)"""
    notification_ids = request.POST.getlist('ids[]')
    if notification_ids:
        Notification.objects.filter(
            recipient=request.user,
            id__in=notification_ids
        ).update(is_read=True)
    return JsonResponse({'success': True})


@login_required
@require_POST
def mark_all_notifications_read(request):
    """Mark all notifications as read (AJAX)"""
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    return JsonResponse({'success': True})


@login_required
def get_unread_counts(request):
    """Get unread counts for notifications badge (AJAX polling)"""
    user = request.user

    user_chats = PrivateChat.objects.filter(
        Q(participant1=user) | Q(participant2=user)
    )

    unread_notifications = Notification.objects.filter(
        recipient=user, is_read=False
    ).count()

    unread_messages = PrivateMessage.objects.filter(
        chat__in=user_chats,
        is_read=False,
    ).exclude(sender=user).count()

    pending_friend_requests = Friendship.objects.filter(
        to_user=user, status='pending'
    ).count()

    # Pending join requests for groups user admins
    user_groups = StudyGroup.objects.filter(members=user)
    admin_groups = user_groups.filter(Q(creator=user) | Q(admins=user))
    pending_join_requests = GroupJoinRequest.objects.filter(
        group__in=admin_groups, status='pending'
    ).distinct().count()

    return JsonResponse({
        'notifications': unread_notifications,
        'messages': unread_messages,
        'friend_requests': pending_friend_requests,
        'join_requests': pending_join_requests,
        'total': unread_notifications + unread_messages + pending_friend_requests,
    })
