from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.inclusion_tag('users/avatar.html')
def user_avatar(user, size='md', css_class=''):
    """
    Render a user avatar with profile picture or default initials
    
    Usage: {% user_avatar user size="lg" css_class="extra-class" %}
    
    Sizes: sm (30px), md (40px), lg (50px), xl (60px), xxl (120px)
    """
    size_map = {
        'sm': '30px',
        'md': '40px',
        'lg': '50px',
        'xl': '60px',
        'xxl': '120px'
    }
    
    avatar_size = size_map.get(size, '40px')
    
    # Get profile picture URL
    profile_picture_url = None
    initials = user.username[0].upper()
    
    if hasattr(user, 'profile'):
        profile_picture_url = user.profile.get_profile_picture_url()
        if hasattr(user.profile, 'get_initials'):
            initials = user.profile.get_initials()
    
    return {
        'user': user,
        'profile_picture_url': profile_picture_url,
        'initials': initials,
        'size': avatar_size,
        'css_class': css_class,
    }
