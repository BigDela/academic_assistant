# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from .models import CustomUser, UserProfile

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'course', 'year')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'course', 'year')


class ProfileEditForm(forms.ModelForm):
    """Form for editing user profile information"""
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio', 'program_of_study', 'year_level', 'theme_preference']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell us about yourself...',
                'class': 'form-control'
            }),
            'program_of_study': forms.TextInput(attrs={
                'placeholder': 'e.g., Computer Science',
                'class': 'form-control'
            }),
            'year_level': forms.TextInput(attrs={
                'placeholder': 'e.g., Sophomore',
                'class': 'form-control'
            }),
        }
    
    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            # Validate file size (max 5MB)
            if picture.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Profile picture must be less than 5MB")
            
            # Validate file type
            valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if picture.content_type not in valid_types:
                raise forms.ValidationError("Only JPEG, PNG, and GIF images are allowed")
        
        return picture


class UserInfoEditForm(forms.ModelForm):
    """Form for editing basic user information"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'your.email@example.com'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id', None)
        super().__init__(*args, **kwargs)
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Check if username is already taken by another user
        if User.objects.filter(username=username).exclude(id=self.user_id).exists():
            raise forms.ValidationError("This username is already taken.")
        
        # Validate username format
        if not username.isalnum() and '_' not in username:
            raise forms.ValidationError("Username can only contain letters, numbers, and underscores.")
        
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if email is already taken by another user
        if User.objects.filter(email=email).exclude(id=self.user_id).exists():
            raise forms.ValidationError("This email is already registered.")
        
        return email


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with better styling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Current Password'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'New Password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm New Password'
        })
