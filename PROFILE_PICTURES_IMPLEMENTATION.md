# Profile Pictures Implementation Guide

## Overview
Profile pictures are implemented globally across the Academic Assistant platform. Every user display includes their profile picture with a fallback to initials-based default avatars.

## Backend Infrastructure

### Model Structure
- **UserProfile Model** (`users/models.py`)
  - `profile_picture` field: `ImageField(upload_to='profile_pictures/%Y/%m/', null=True, blank=True)`
  - `get_profile_picture_url()`: Returns profile picture URL or None
  - `get_initials()`: Returns user initials for default avatars

### Media Configuration
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"
```

Media files are served in DEBUG mode via `static()` in `urls.py`:
```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Signals
Auto-creation of UserProfile on user registration (`users/signals.py`):
- `create_user_profile`: Creates profile on user save
- `save_user_profile`: Saves profile on user save

## Frontend Implementation

### Template Display Pattern
Standard pattern used across all templates:
```django
{% if user.profile.profile_picture %}
<img src="{{ user.profile.profile_picture.url }}" alt="{{ user.username }}" class="user-avatar">
{% else %}
<div class="user-avatar user-avatar-default">{{ user.username.0|upper }}</div>
{% endif %}
```

### Custom Template Tag
Reusable avatar component (`users/templatetags/avatar_tags.py`):
```django
{% load avatar_tags %}
{% user_avatar user size="md" css_class="extra-class" %}
```

Supported sizes: `sm` (30px), `md` (40px), `lg` (50px), `xl` (60px), `xxl` (120px)

### Global CSS Classes
Defined in `static/css/main.css`:

**Base Avatar Class:**
```css
.user-avatar {
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
}
```

**Size Classes:**
- `.avatar-sm`: 30px × 30px
- `.avatar-md`: 40px × 40px (default)
- `.avatar-lg`: 50px × 50px
- `.avatar-xl`: 60px × 60px
- `.avatar-xxl`: 120px × 120px

**Default Avatar (Initials):**
```css
.user-avatar-default {
    background: linear-gradient(135deg, var(--primary-blue), var(--accent-blue));
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
}
```

## Profile Picture Locations

### Navigation & Header
- **base.html**: User menu avatar (top-right dropdown)

### User Profile Pages
- **profile.html**: Current user's profile header
- **profile_edit.html**: Profile edit page (2 locations - view and upload)
- **public_profile.html**: Other users' public profiles

### Social Features
- **friends_list.html**: 4 locations
  - Friend request cards
  - Current friends list
  - Pending requests
  - Suggested friends

- **private_chats_list.html**: Chat overview list
- **private_chat.html**: Chat header with other user's avatar
- **discover_users.html**: Discovery cards (swipe interface)

### Study Groups
- **group_join_requests.html**: Join request cards
- **group_chat.html**: Members sidebar list
- **group_detail.html**: Group members (if applicable)

## Styling Guidelines

### Circular Shape
All profile pictures use `border-radius: 50%` for circular display.

### Image Fit
`object-fit: cover` ensures images fill the circular container without distortion.

### Flex Behavior
`flex-shrink: 0` prevents avatars from shrinking in flex containers.

### Default Avatar Gradient
Initials display on gradient background:
```css
background: linear-gradient(135deg, var(--primary-blue), var(--accent-blue));
```

### Size Consistency
- **Large displays** (profiles, discovery): 120px+
- **Medium displays** (lists, headers): 40-60px
- **Small displays** (inline mentions): 30px

## Upload & Update Workflow

### Profile Picture Upload
1. User navigates to profile edit page
2. Selects new image via file input
3. Form submits to `profile_edit` view
4. Image saved to `media/profile_pictures/YYYY/MM/filename`
5. UserProfile model updated with new path

### Dynamic Updates
Profile pictures update across all pages after:
- Page refresh/reload
- Navigation to different views
- Real-time updates via Pusher (for chat interfaces)

### File Constraints
- Max file size: 10MB (can be configured in form validation)
- Supported formats: JPEG, PNG, GIF, WebP
- Stored path: `profile_pictures/%Y/%m/` (organized by year/month)

## Testing Checklist

### Visual Verification
- [ ] Profile page shows correct avatar
- [ ] Friends list shows avatars for all users
- [ ] Chat lists show correct participant avatars
- [ ] Private chat shows other user's avatar in header
- [ ] Group chat shows member avatars in sidebar
- [ ] Discovery cards show user avatars
- [ ] Join request cards show requester avatars
- [ ] Base navigation shows current user's avatar

### Functional Testing
- [ ] Upload new profile picture
- [ ] Verify picture updates on profile page
- [ ] Navigate to friends list - picture updated
- [ ] Open chats - picture updated in headers/lists
- [ ] Check other users' public profiles
- [ ] Verify default initials display when no picture

### Edge Cases
- [ ] New user without profile picture shows initials
- [ ] Deleted/missing image file shows initials
- [ ] Very large images are resized/optimized
- [ ] Non-square images are cropped correctly (object-fit: cover)
- [ ] Profile pictures work in all browsers

## Migration to Template Tags

### Current Implementation
Most templates use inline profile picture checks:
```django
{% if user.profile.profile_picture %}
    <img src="{{ user.profile.profile_picture.url }}">
{% else %}
    <div>{{ user.username.0|upper }}</div>
{% endif %}
```

### Recommended Migration
Replace with template tag for consistency:
```django
{% load avatar_tags %}
{% user_avatar user size="md" %}
```

### Benefits
- Centralized avatar logic
- Consistent styling across templates
- Easier maintenance
- Reduced code duplication
- Built-in size management

## Troubleshooting

### Profile Picture Not Displaying
1. Check `MEDIA_URL` and `MEDIA_ROOT` in settings
2. Verify `static()` is added to urlpatterns in DEBUG mode
3. Ensure UserProfile exists for user (signals should create automatically)
4. Check file permissions on `media/profile_pictures/` directory
5. Verify image file exists at stored path

### Initials Not Showing
1. Check `get_initials()` method in UserProfile model
2. Verify `.user-avatar-default` CSS class exists
3. Ensure username exists and is not empty

### Image Distorted
1. Add `object-fit: cover` to avatar CSS
2. Ensure container has fixed width/height
3. Check `border-radius: 50%` is applied

### Profile Picture Not Updating
1. Hard refresh browser (Ctrl+F5)
2. Check Django's file storage is writing to correct path
3. Verify old file is replaced or filename is unique
4. Clear browser cache

## Future Enhancements

### Performance Optimization
- Implement image thumbnail generation (e.g., using Pillow)
- Create multiple sizes at upload time (30px, 60px, 120px)
- Use WebP format for smaller file sizes
- Add CDN for media file serving in production

### Real-Time Updates
- Pusher events when profile picture changes
- Auto-update avatars without page refresh
- Websocket integration for live updates

### Advanced Features
- Image cropping/editing interface before upload
- Avatar frame/border customization
- Animated profile pictures (GIFs)
- Profile picture history/gallery
- AI-generated default avatars (beyond initials)

## Code Maintenance

### Adding Profile Pictures to New Templates
1. Pass user object to template context
2. Use standard pattern or template tag
3. Apply appropriate size class
4. Test with and without profile picture

### Updating Avatar Styling
1. Modify `static/css/main.css` (Section 0: USER AVATARS)
2. Update size classes if needed
3. Test across all templates
4. Consider updating template tag if sizes change

### Backend Changes
1. Model changes require migrations: `python manage.py makemigrations && python manage.py migrate`
2. Update `get_profile_picture_url()` or `get_initials()` as needed
3. Test signals if modifying user creation flow

---

**Last Updated**: [Current Date]
**Maintainer**: Development Team
