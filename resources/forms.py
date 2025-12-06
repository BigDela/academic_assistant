from django import forms
from .models import Document, StudyGroup, Message, GroupInvite, Friendship, PrivateMessage, MessageReaction, MessageAttachment
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models as django_models

User = get_user_model()

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type your message...'})
        }

class StudyGroupForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = ['name', 'description']

class DocumentUploadForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=StudyGroup.objects.none(), required=False, empty_label="No group (public)")

    class Meta:
        model = Document
        fields = ['title', 'file', 'course', 'tags', 'group']
        widgets = {
            'course': forms.TextInput(attrs={'placeholder': 'Enter course name'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Only show groups where the user is a member
            self.fields['group'].queryset = user.study_groups.all()

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file.size > 10 * 1024 * 1024:  # 10MB max
            raise forms.ValidationError("File too large. Max size is 10MB.")
        return file

class EditGroupForm(forms.ModelForm):
    """Form for editing group information"""
    class Meta:
        model = StudyGroup
        fields = ['name', 'description', 'is_invite_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your study group...'})
        }

class ManagePermissionsForm(forms.Form):
    """Form for managing admin and editor permissions"""
    admins = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Admins (can manage members and edit group)"
    )
    editors = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Editors (can edit group info)"
    )

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        if group:
            # Only show group members (excluding creator)
            members = group.members.exclude(id=group.creator.id)
            self.fields['admins'].queryset = members
            self.fields['editors'].queryset = members

class CreateInviteForm(forms.ModelForm):
    """Form for creating custom invite links"""
    class Meta:
        model = GroupInvite
        fields = ['expires_at', 'max_uses']
        widgets = {
            'expires_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'max_uses': forms.NumberInput(attrs={'min': 1, 'placeholder': 'Leave empty for unlimited'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expires_at'].required = False
        self.fields['max_uses'].required = False

class JoinGroupCodeForm(forms.Form):
    """Form for joining group via invite code"""
    invite_code = forms.CharField(
        max_length=12,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 12-character invite code',
            'style': 'text-transform: uppercase;'
        })
    )
    
    def clean_invite_code(self):
        code = self.cleaned_data.get('invite_code', '').upper().strip()
        if len(code) != 12:
            raise forms.ValidationError("Invite code must be 12 characters long.")
        return code


# ============ PRIVATE MESSAGING FORMS ============

class AddFriendForm(forms.Form):
    """Form for adding friends by username"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter username',
            'class': 'friend-search-input'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Check if user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("User not found.")
        
        # Check if trying to add self
        if self.current_user and user == self.current_user:
            raise forms.ValidationError("You cannot add yourself as a friend.")
        
        # Check if already friends or request pending
        if self.current_user:
            existing = Friendship.objects.filter(
                django_models.Q(from_user=self.current_user, to_user=user) |
                django_models.Q(from_user=user, to_user=self.current_user)
            ).first()
            
            if existing:
                if existing.status == 'accepted':
                    raise forms.ValidationError("You are already friends with this user.")
                elif existing.status == 'pending':
                    raise forms.ValidationError("Friend request is already pending.")
                elif existing.status == 'blocked':
                    raise forms.ValidationError("Cannot send friend request to this user.")
        
        return username


class PrivateMessageForm(forms.ModelForm):
    """Form for sending private messages"""
    class Meta:
        model = PrivateMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Type your message...',
                'class': 'message-input'
            })
        }


class MessageAttachmentForm(forms.ModelForm):
    """Form for uploading message attachments"""
    class Meta:
        model = MessageAttachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'accept': '.pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif,.zip,.rar',
                'class': 'file-input'
            })
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Max file size: 25MB
            if file.size > 25 * 1024 * 1024:
                raise forms.ValidationError("File too large. Max size is 25MB.")
            
            # Store filename and metadata
            self.cleaned_data['filename'] = file.name
            self.cleaned_data['file_size'] = file.size
            self.cleaned_data['file_type'] = file.content_type
        
        return file


class MessageReactionForm(forms.Form):
    """Form for adding reactions to messages"""
    emoji = forms.ChoiceField(
        choices=MessageReaction.EMOJI_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'emoji-picker'})
    )