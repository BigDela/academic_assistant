# URL Routing Test Guide

## Fixed Issues

### 1. URL Path Conflicts ✅
**Problem:** Dynamic username path `profile/<username>/` was catching specific paths like `profile/edit/`

**Solution:** Reordered URLs so specific paths come before dynamic path:
```python
# Correct order (specific → dynamic)
path('profile/', views.profile_view, name='profile'),
path('profile/edit/', views.profile_edit, name='profile_edit'),
path('profile/user-info/', views.user_info_edit, name='user_info_edit'),
path('profile/change-password/', views.change_password, name='change_password'),
path('profile/toggle-theme/', views.toggle_theme, name='toggle_theme'),
path('profile/<str:username>/', views.public_profile_view, name='public_profile'),  # Last
```

### 2. Dark Mode Chat Input ✅
**Problem:** Chat input boxes were affected by dark mode, becoming hard to read

**Solution:** Added explicit CSS rules to keep chat inputs light:
- Message input textboxes stay white background
- Text color remains dark (#2C3E50)
- Placeholders stay gray (#9CA3AF)
- Input containers stay light (#FFFFFF)

**Files Modified:**
- `templates/base.html` - Global dark mode overrides
- `resources/templates/resources/private_chat.html` - Private chat input styles
- `resources/templates/resources/group_chat.html` - Group chat input styles

### 3. Theme Toggle Improvements ✅
**Enhanced:** Theme toggle now:
- Returns to previous page using HTTP_REFERER
- Shows success message when toggling
- Properly persists across all pages

## Test Checklist

### Profile URLs Test
Test these URLs while logged in:

1. **View Own Profile**
   - URL: `/users/profile/`
   - Expected: Shows your profile with edit buttons
   - Status: ✅ Should work

2. **Edit Profile**
   - URL: `/users/profile/edit/`
   - Expected: Form to edit bio, profile picture, etc.
   - Status: ✅ Should work

3. **Edit User Info**
   - URL: `/users/profile/user-info/`
   - Expected: Form to edit username, email, name
   - Status: ✅ Should work

4. **Change Password**
   - URL: `/users/profile/change-password/`
   - Expected: Password change form
   - Status: ✅ Should work

5. **Toggle Theme**
   - URL: `/users/profile/toggle-theme/`
   - Expected: Toggles dark/light mode, redirects back
   - Status: ✅ Should work

6. **View Public Profile**
   - URL: `/users/profile/<username>/` (e.g., `/users/profile/Kofi/`)
   - Expected: Shows public profile of another user
   - Status: ✅ Should work

### Dark Mode Test

**Light Mode:**
1. Navigate to profile
2. All backgrounds should be light blue/white
3. Text should be dark
4. Chat inputs should be white with dark text

**Dark Mode:**
1. Click "Toggle Dark Mode" button
2. Page backgrounds should turn dark (#1F2937)
3. Text should turn light (#E5E7EB)
4. **IMPORTANT:** Chat input boxes should REMAIN WHITE with DARK TEXT
5. Toggle back to light mode - everything returns to normal

**Test Chat Inputs Specifically:**
1. Go to private chat: `/resources/chats/<chat_id>/`
2. Toggle dark mode
3. Message input textbox should stay WHITE with DARK text
4. Input should be easily readable
5. Go to group chat: `/resources/groups/<group_id>/chat/`
6. Toggle dark mode
7. Message input should stay WHITE with DARK text

### Navigation Links Test

Test all sidebar navigation links work correctly:

**Main Section:**
- Home: `/` ✅
- Study Groups: `/resources/groups/` ✅
- Documents: `/resources/documents/` ✅

**Social Section:**
- Friends: `/resources/friends/` ✅
- Messages: `/resources/chats/` ✅

**Account Section:**
- Profile: `/users/profile/` ✅

**User Avatar (bottom):**
- Click avatar → Should go to `/users/profile/` ✅

### Profile Action Buttons Test

From your profile page (`/users/profile/`):

1. **Edit Profile Button**
   - Click → Should go to `/users/profile/edit/`
   - Make change → Save → Should return to profile with success message

2. **Edit User Info Button**
   - Click → Should go to `/users/profile/user-info/`
   - Change username → Save → Should update and return to profile

3. **Change Password Button**
   - Click → Should go to `/users/profile/change-password/`
   - Change password → Should update session (no logout)

4. **Toggle Theme Button**
   - Click → Should toggle dark/light mode
   - Should stay on profile page
   - Success message should appear

### Public Profile Links Test

1. Go to friends list: `/resources/friends/`
2. Click on any friend's name or avatar
3. Should go to `/users/profile/<username>/`
4. Should show their public profile
5. If friends: Should see "Send Message" button
6. If not friends: Should see "Add Friend" button

### Mobile Responsive Test

**Desktop (>968px):**
- Sidebar visible on left
- Can collapse sidebar with toggle button
- Profile avatar visible in sidebar footer

**Mobile (<968px):**
- Sidebar hidden by default
- Hamburger menu button visible (top-left)
- Click hamburger → Sidebar slides in from left
- Dark overlay appears
- Click overlay → Sidebar closes

## Common Issues & Solutions

### Issue: "profile/edit/" showing public profile
**Cause:** Dynamic path catching specific paths
**Fix:** ✅ Already fixed - specific paths before dynamic

### Issue: Chat input unreadable in dark mode
**Cause:** CSS variables affecting input background
**Fix:** ✅ Already fixed - explicit white background with !important

### Issue: Theme doesn't persist
**Cause:** UserProfile not created or context processor missing
**Fix:** Context processor already added in settings.py

### Issue: Toggle theme redirects to wrong page
**Cause:** Using query parameter instead of referer
**Fix:** ✅ Already fixed - uses HTTP_REFERER

### Issue: 404 on profile/edit
**Cause:** URL ordering or missing import
**Check:**
1. URLs are in correct order ✅
2. View is imported in urls.py ✅
3. View exists in views.py ✅

## Testing Commands

### Test URL Routing
```python
# In Django shell
python manage.py shell

from django.urls import reverse
print(reverse('profile'))  # Should print: /users/profile/
print(reverse('profile_edit'))  # Should print: /users/profile/edit/
print(reverse('public_profile', args=['testuser']))  # Should print: /users/profile/testuser/
```

### Test Theme Toggle
```python
# In Django shell
from django.contrib.auth import get_user_model
from users.models import UserProfile

User = get_user_model()
user = User.objects.first()
profile = UserProfile.objects.get(user=user)

print(f"Current theme: {profile.theme_preference}")
profile.theme_preference = 'dark' if profile.theme_preference == 'light' else 'light'
profile.save()
print(f"New theme: {profile.theme_preference}")
```

## CSS Variables Reference

### Light Mode
```css
--primary-blue: #4A90E2
--light-blue: #E8F4FD
--text-dark: #2C3E50
--text-gray: #6B7280
--white: #FFFFFF
```

### Dark Mode
```css
--primary-blue: #5BA3F5
--light-blue: #1E3A5F
--text-dark: #E5E7EB
--text-gray: #9CA3AF
--white: #1F2937
```

### Always Light (Chat Inputs)
```css
background: #FFFFFF !important
color: #2C3E50 !important
border-color: #E5E7EB !important
```

## Files Modified

1. ✅ `users/urls.py` - Reordered URL patterns
2. ✅ `users/views.py` - Improved toggle_theme view
3. ✅ `templates/base.html` - Added dark mode input overrides
4. ✅ `resources/templates/resources/private_chat.html` - Explicit input colors
5. ✅ `resources/templates/resources/group_chat.html` - Explicit input colors

## Success Criteria

All tests pass when:
- ✅ All profile URLs resolve correctly
- ✅ No 404 errors on profile management pages
- ✅ Dark mode applies to all pages except chat inputs
- ✅ Chat inputs remain readable in dark mode
- ✅ Theme toggle persists across page navigations
- ✅ Profile pictures display in sidebar and throughout app
- ✅ Public profiles accessible via username
- ✅ Mobile menu works smoothly
