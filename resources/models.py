# Create your models here.
from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from django.db.models import Q
import uuid


class Course(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Document(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    course = models.CharField(max_length=200)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    group = models.ForeignKey('StudyGroup', on_delete=models.CASCADE, null=True, blank=True, related_name='documents')

    def __str__(self):
        return self.title


class StudyGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='study_groups')
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='admin_groups', blank=True)
    editors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='editor_groups', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    invite_code = models.CharField(max_length=12, unique=True, blank=True)
    is_invite_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self.generate_invite_code()
        super().save(*args, **kwargs)
    
    def generate_invite_code(self):
        code = get_random_string(12).upper()
        while StudyGroup.objects.filter(invite_code=code).exists():
            code = get_random_string(12).upper()
        return code
    
    def is_admin(self, user):
        return user == self.creator or user in self.admins.all()
    
    def is_editor(self, user):
        return self.is_admin(user) or user in self.editors.all()
    
    def can_manage_members(self, user):
        return self.is_admin(user)
    
    def can_edit_group(self, user):
        return self.is_editor(user)

class GroupInvite(models.Model):
    """Model for tracking group invite links with expiration"""
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='invites')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    invite_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    max_uses = models.IntegerField(null=True, blank=True, help_text="Maximum number of times this invite can be used")
    uses_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Invite to {self.group.name} by {self.created_by.username}"
    
    def can_be_used(self):
        """Check if invite is still valid"""
        from django.utils import timezone
        
        if not self.is_active:
            return False
        
        if self.expires_at and self.expires_at < timezone.now():
            return False
        
        if self.max_uses and self.uses_count >= self.max_uses:
            return False
        
        return True
    
    def use_invite(self):
        """Increment use count"""
        self.uses_count += 1
        self.save()

class Message(models.Model):
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_edited = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"
    
    def get_reactions_summary(self):
        """Get a summary of reactions grouped by emoji"""
        from django.db.models import Count
        return self.reactions.values('emoji').annotate(count=Count('emoji'))


class Friendship(models.Model):
    """Model for managing friend relationships"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('blocked', 'Blocked'),
    ]
    
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.status})"
    
    @classmethod
    def are_friends(cls, user1, user2):
        """Check if two users are friends"""
        return cls.objects.filter(
            Q(from_user=user1, to_user=user2, status='accepted') |
            Q(from_user=user2, to_user=user1, status='accepted')
        ).exists()
    
    @classmethod
    def get_friends(cls, user):
        """Get all friends of a user"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        friend_ids = []
        friendships = cls.objects.filter(
            Q(from_user=user, status='accepted') |
            Q(to_user=user, status='accepted')
        )
        
        for friendship in friendships:
            if friendship.from_user == user:
                friend_ids.append(friendship.to_user.id)
            else:
                friend_ids.append(friendship.from_user.id)
        
        return User.objects.filter(id__in=friend_ids)


class PrivateChat(models.Model):
    """Model for one-on-one private conversations"""
    participant1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='private_chats_as_participant1')
    participant2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='private_chats_as_participant2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat: {self.participant1.username} & {self.participant2.username}"
    
    def get_other_participant(self, user):
        """Get the other participant in the chat"""
        return self.participant2 if self.participant1 == user else self.participant1
    
    @classmethod
    def get_or_create_chat(cls, user1, user2):
        """Get existing chat or create new one between two users"""
        chat = cls.objects.filter(
            Q(participant1=user1, participant2=user2) |
            Q(participant1=user2, participant2=user1)
        ).first()
        
        if not chat:
            chat = cls.objects.create(participant1=user1, participant2=user2)
        
        return chat


class PrivateMessage(models.Model):
    """Model for private messages between users"""
    chat = models.ForeignKey(PrivateChat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_private_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_edited = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username} to {self.chat.get_other_participant(self.sender).username}: {self.content[:30]}"
    
    def get_reactions_summary(self):
        """Get a summary of reactions grouped by emoji"""
        from django.db.models import Count
        return self.reactions.values('emoji').annotate(count=Count('emoji'))


class MessageReaction(models.Model):
    """Model for emoji reactions to messages"""
    EMOJI_CHOICES = [
        ('👍', 'Thumbs Up'),
        ('❤️', 'Heart'),
        ('😂', 'Laugh'),
        ('😮', 'Wow'),
        ('😢', 'Sad'),
        ('🔥', 'Fire'),
        ('👏', 'Clap'),
        ('🎉', 'Party'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=10, choices=EMOJI_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Polymorphic relation - can react to group or private messages
    group_message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True, related_name='reactions')
    private_message = models.ForeignKey(PrivateMessage, on_delete=models.CASCADE, null=True, blank=True, related_name='reactions')

    class Meta:
        unique_together = [
            ('user', 'group_message', 'emoji'),
            ('user', 'private_message', 'emoji'),
        ]

    def __str__(self):
        if self.group_message:
            return f"{self.user.username} reacted {self.emoji} to group message"
        return f"{self.user.username} reacted {self.emoji} to private message"


class MessageAttachment(models.Model):
    """Model for file attachments in messages"""
    file = models.FileField(upload_to='message_attachments/%Y/%m/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text="File size in bytes")
    file_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Polymorphic relation - can attach to group or private messages
    group_message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments')
    private_message = models.ForeignKey(PrivateMessage, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments')

    def __str__(self):
        return f"Attachment: {self.filename}"
    
    def get_file_size_display(self):
        """Return human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    
class GroupChat(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='group_chats')

    def __str__(self):
        return self.name


class UserDiscoveryAction(models.Model):
    """Track user discovery actions (swipe/accept/reject)"""
    ACTION_CHOICES = [
        ('accept', 'Accept'),
        ('reject', 'Reject'),
        ('skip', 'Skip'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discovery_actions')
    discovered_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discovered_by')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'discovered_user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} {self.action}ed {self.discovered_user.username}"


class GroupDiscoveryAction(models.Model):
    """Track group discovery actions"""
    ACTION_CHOICES = [
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
        ('skip', 'Skip'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_discovery_actions')
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='discovery_actions')
    action = models.CharField(max_length=15, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'group')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} {self.action} in {self.group.name}"


class GroupJoinRequest(models.Model):
    """Handle group join requests from discovery"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_join_requests')
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='join_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, help_text="Optional message to group admins")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_join_requests')

    class Meta:
        unique_together = ('user', 'group')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} -> {self.group.name} ({self.status})"


class Notification(models.Model):
    """Unified notification model for all activity events"""
    NOTIFICATION_TYPES = [
        ('group_message', 'New Group Message'),
        ('private_message', 'New Private Message'),
        ('friend_request', 'Friend Request Received'),
        ('friend_accepted', 'Friend Request Accepted'),
        ('group_join_request', 'Group Join Request'),
        ('group_join_approved', 'Group Join Approved'),
        ('group_join_rejected', 'Group Join Rejected'),
        ('member_joined', 'Member Joined Group'),
        ('document_shared', 'Document Shared'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Optional references to related objects
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='sent_notifications'
    )
    group = models.ForeignKey(
        StudyGroup, on_delete=models.CASCADE, null=True, blank=True
    )
    private_chat = models.ForeignKey(
        PrivateChat, on_delete=models.CASCADE, null=True, blank=True
    )

    # URL to navigate to when clicking the notification
    action_url = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]

    def __str__(self):
        return f"[{self.notification_type}] {self.title} → {self.recipient.username}"