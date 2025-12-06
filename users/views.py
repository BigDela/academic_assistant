from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, ProfileEditForm, UserInfoEditForm, CustomPasswordChangeForm
from .models import UserProfile

User = get_user_model()

# Create your views here.
# users/views.py


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'users/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        # Create profile for new user
        UserProfile.objects.get_or_create(user=self.object)
        messages.success(self.request, "Signed up successfully!")
        return response


@login_required
def profile_view(request):
    """View user's own profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'profile': profile,
        'user': request.user,
        'is_own_profile': True,
    }
    return render(request, 'users/profile.html', context)


@login_required
def public_profile_view(request, username):
    """View another user's public profile"""
    user = get_object_or_404(User, username=username)
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Check if users are friends
    from resources.models import Friendship
    are_friends = Friendship.are_friends(request.user, user) if request.user != user else False
    
    context = {
        'profile': profile,
        'user': user,
        'profile_user': user,  # For clarity in template
        'is_own_profile': request.user == user,
        'are_friends': are_friends,
    }
    return render(request, 'users/public_profile.html', context)


@login_required
def profile_edit(request):
    """Edit user profile information"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'users/profile_edit.html', context)


@login_required
def user_info_edit(request):
    """Edit basic user information (username, email, name)"""
    if request.method == 'POST':
        form = UserInfoEditForm(request.POST, instance=request.user, user_id=request.user.id)
        if form.is_valid():
            form.save()
            messages.success(request, "User information updated successfully!")
            return redirect('profile')
    else:
        form = UserInfoEditForm(instance=request.user, user_id=request.user.id)
    
    context = {
        'form': form,
    }
    return render(request, 'users/user_info_edit.html', context)


@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update session to prevent logout
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully!")
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'users/change_password.html', context)


@login_required
def toggle_theme(request):
    """Toggle between light and dark mode"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if profile.theme_preference == 'light':
        profile.theme_preference = 'dark'
    else:
        profile.theme_preference = 'light'
    
    profile.save()
    
    # Return to previous page or profile
    next_url = request.GET.get('next', 'profile')
    return redirect(next_url)
