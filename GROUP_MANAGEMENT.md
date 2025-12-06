# Group Management Features - Implementation Guide

## Overview
Comprehensive group management system for study groups with role-based permissions, member management, and flexible invite system.

## Features Implemented

### 1. Role-Based Permissions

#### Roles
- **Creator**: Original group creator (automatically has all permissions)
- **Admin**: Can manage members, edit group, create invites, remove members
- **Editor**: Can only edit group information (name, description)
- **Member**: Regular group member (can access chat and documents)

#### Permission Methods (StudyGroup model)
```python
group.is_admin(user)         # Check if user is admin or creator
group.is_editor(user)        # Check if user is editor, admin, or creator
group.can_manage_members(user)  # Check if user can add/remove members
group.can_edit_group(user)   # Check if user can edit group info
```

### 2. Group Management Actions

#### Edit Group (`/resources/groups/<id>/edit/`)
- **Who can access**: Creator, Admins, Editors
- **What can be edited**:
  - Group name
  - Description
  - Invite code activation status
- **Template**: `resources/edit_group.html`
- **Form**: `EditGroupForm`

#### Delete Group (`/resources/groups/<id>/delete/`)
- **Who can access**: Creator only
- **What happens**:
  - All messages are deleted (cascade)
  - All documents associated with group are deleted
  - All member associations are removed
  - All invites are deleted
- **Template**: `resources/delete_group.html`

#### Leave Group (`/resources/groups/<id>/leave/`)
- **Who can access**: All members except creator
- **What happens**:
  - User is removed from members
  - User is removed from admins (if applicable)
  - User is removed from editors (if applicable)
- **Template**: `resources/leave_group.html`

### 3. Member Management

#### Manage Permissions (`/resources/groups/<id>/permissions/`)
- **Who can access**: Creator and Admins
- **What can be managed**:
  - Assign/revoke admin roles
  - Assign/revoke editor roles
  - Creator cannot be assigned roles (has all permissions by default)
- **Template**: `resources/manage_permissions.html`
- **Form**: `ManagePermissionsForm` (dynamically filtered to show only current members)

#### Remove Member (`/resources/groups/<id>/remove/<user_id>/`)
- **Who can access**: Creator and Admins
- **Restrictions**:
  - Cannot remove the creator
  - Member is removed from all roles (member, admin, editor)
- **Template**: `resources/remove_member.html`

### 4. Invite System

#### Quick Invite Code
- **Auto-generated**: Every group gets a unique 12-character code on creation
- **Format**: Uppercase alphanumeric (e.g., `ABC123XYZ789`)
- **Access**: Share via "Join via Code" button on group list
- **URL**: `/resources/join-code/`
- **Can be disabled**: Via `is_invite_active` field in group settings

#### Custom Invite Links
- **Who can create**: Creator and Admins
- **Features**:
  - Optional expiration date
  - Optional usage limit (max number of uses)
  - Unique UUID token
  - Can be deactivated manually
  - Tracks usage count

#### Invite Management (`/resources/groups/<id>/invites/`)
- **Who can access**: Creator and Admins
- **What you can see**:
  - Quick invite code with copy button
  - List of all custom invite links
  - Status of each invite (active/inactive/expired)
  - Usage statistics
- **Actions**:
  - Create new custom invite link
  - Deactivate existing invite links
  - View full invite URLs

#### Join via Invite Link (`/resources/invite/<token>/`)
- **Public access**: Anyone with the link
- **Validation**:
  - Checks if invite is active
  - Checks expiration date
  - Checks usage limit
  - Increments usage counter on successful join

#### Join via Code (`/resources/join-code/`)
- **Public access**: Any logged-in user
- **Form**: Enter 12-character code
- **Validation**:
  - Code must exist
  - Group must have `is_invite_active=True`
- **Template**: `resources/join_via_code.html`

## Database Schema

### StudyGroup Model Updates
```python
admins = ManyToManyField(User, related_name='admin_groups', blank=True)
editors = ManyToManyField(User, related_name='editor_groups', blank=True)
invite_code = CharField(max_length=12, unique=True, blank=True)
is_invite_active = BooleanField(default=True)
```

### New Model: GroupInvite
```python
group = ForeignKey(StudyGroup, on_delete=CASCADE, related_name='invites')
created_by = ForeignKey(User, on_delete=CASCADE)
invite_token = UUIDField(default=uuid4, unique=True, editable=False)
created_at = DateTimeField(auto_now_add=True)
expires_at = DateTimeField(null=True, blank=True)
max_uses = IntegerField(null=True, blank=True)
uses_count = IntegerField(default=0)
is_active = BooleanField(default=True)
```

## URL Patterns

```python
# Group management
path('groups/<int:group_id>/edit/', views.edit_group, name='edit_group')
path('groups/<int:group_id>/delete/', views.delete_group, name='delete_group')
path('groups/<int:group_id>/leave/', views.leave_group, name='leave_group')

# Permissions and members
path('groups/<int:group_id>/permissions/', views.manage_permissions, name='manage_permissions')
path('groups/<int:group_id>/remove/<int:user_id>/', views.remove_member, name='remove_member')

# Invites
path('groups/<int:group_id>/invites/', views.group_invites, name='group_invites')
path('groups/<int:group_id>/invites/create/', views.create_invite_link, name='create_invite_link')
path('invites/<int:invite_id>/deactivate/', views.deactivate_invite, name='deactivate_invite')
path('invite/<uuid:invite_token>/', views.join_via_invite_link, name='join_via_invite_link')
path('join-code/', views.join_via_code, name='join_via_code')
```

## Views Implementation

All views include proper:
- Authentication checks (`@login_required`)
- Permission validation
- Error handling with user-friendly messages
- Redirect patterns

### Security Features
1. **Permission checks**: Every action validates user permissions
2. **Creator protection**: Creator cannot be removed or leave group
3. **Invite validation**: Checks expiration, usage limits, active status
4. **SQL injection protection**: All database queries use Django ORM
5. **CSRF protection**: All forms include CSRF tokens

## UI Integration

### Group Detail Page Updates
New action buttons visible based on user role:
- **For all members**: "Open Chat", "Leave Group" (non-creators)
- **For editors**: "Edit Group"
- **For admins**: "Manage Permissions", "Invites"
- **For creator**: All above plus "Delete Group"

### Group List Page Updates
- New "Join via Code" button in header
- Easy access to quick join functionality

### Template Design
- Consistent light-blue theme
- Card-based layouts
- Responsive design
- Clear visual hierarchy
- Status badges (active/inactive)
- Copy-to-clipboard functionality for invite codes

## Testing Checklist

### Basic Functionality
- [ ] Create group and verify invite code is generated
- [ ] Edit group as creator, admin, editor
- [ ] Verify non-editors cannot edit group
- [ ] Delete group (creator only)
- [ ] Leave group (non-creator members)

### Permission Management
- [ ] Assign admin role to member
- [ ] Assign editor role to member
- [ ] Verify admin can manage members
- [ ] Verify editor can only edit group info
- [ ] Remove member as admin

### Invite System
- [ ] Join via quick invite code
- [ ] Create custom invite link with expiration
- [ ] Create custom invite link with usage limit
- [ ] Join via custom invite link
- [ ] Verify expired invites cannot be used
- [ ] Verify invite with max uses stops working after limit
- [ ] Deactivate invite link
- [ ] Copy invite code to clipboard

### Edge Cases
- [ ] Try to remove group creator (should fail)
- [ ] Try to edit group without permission (should fail)
- [ ] Creator tries to leave group (should fail)
- [ ] Use inactive invite code (should fail)
- [ ] Use expired invite link (should fail)

## Migration Notes

Migration `0007_studygroup_admins_studygroup_editors_and_more.py` includes:
1. Add new fields to StudyGroup
2. **Data migration**: Auto-generate invite codes for existing groups
3. Add unique constraint to invite_code
4. Create GroupInvite model

The data migration ensures no existing groups have null/duplicate invite codes.

## Future Enhancements

Potential improvements:
1. **Transfer ownership**: Allow creator to transfer ownership to another admin
2. **Bulk member actions**: Add/remove multiple members at once
3. **Invite analytics**: Track which invites brought in which members
4. **Role templates**: Pre-defined permission sets for different group types
5. **Member requests**: Require approval for join requests
6. **Audit log**: Track all permission changes and member actions
7. **Email invites**: Send invite links via email
8. **Group privacy levels**: Public, private, secret groups
9. **Member limits**: Set maximum member count per group
10. **Custom roles**: Allow creators to define custom roles beyond admin/editor

## API Documentation

### Permission Check Examples

```python
# In views
if not group.can_edit_group(request.user):
    messages.error(request, "Permission denied")
    return redirect('group_detail', group_id=group.id)

# In templates
{% if user == group.creator or user in group.admins.all %}
    <a href="{% url 'manage_permissions' group.id %}">Manage Permissions</a>
{% endif %}
```

### Invite Validation Example

```python
invite = get_object_or_404(GroupInvite, invite_token=token)

if not invite.can_be_used():
    messages.error(request, "This invite link is no longer valid.")
    return redirect('group_list')

# Join user and increment counter
group.members.add(request.user)
invite.use_invite()
```

## Support & Troubleshooting

### Common Issues

**Issue**: Invite code not working
- Check `is_invite_active` is True
- Verify code is exactly 12 characters
- Check for typos (code is case-sensitive)

**Issue**: Cannot edit group
- Verify user is creator, admin, or editor
- Check database: `group.editors.all()` or `group.admins.all()`

**Issue**: Member removal fails
- Cannot remove creator
- Ensure you have admin permissions

**Issue**: Custom invite link expired
- Check `expires_at` field
- Create new invite link if needed

## Code Organization

```
resources/
├── models.py                 # StudyGroup, GroupInvite models
├── forms.py                  # Management forms
├── views.py                  # All view functions
├── urls.py                   # URL routing
├── admin.py                  # Admin registration
└── templates/resources/
    ├── edit_group.html
    ├── delete_group.html
    ├── leave_group.html
    ├── manage_permissions.html
    ├── remove_member.html
    ├── group_invites.html
    ├── create_invite.html
    └── join_via_code.html
```

---

**Version**: 1.0  
**Date**: December 6, 2025  
**Author**: Academic Assistant Development Team
