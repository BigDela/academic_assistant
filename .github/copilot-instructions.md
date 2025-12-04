# Academic Assistant - AI Agent Instructions

## Project Overview
Django 6.0 academic resource-sharing platform enabling students to upload documents, join study groups, and participate in real-time group chats. Two core apps: `users` (authentication with custom user model) and `resources` (documents, groups, messaging).

## Architecture & Key Components

### Design System
- **Color Theme**: Light blue palette with primary blue (#4A90E2), light blue backgrounds (#E8F4FD), and clean white cards
- **Typography**: Inter font family for modern, clean aesthetics
- **Layout**: Responsive card-based design with consistent spacing and shadows
- **UI Style**: Minimal, modern, uncluttered - inspired by contemporary web apps

### Custom User Model
- **Critical**: Uses `CustomUser` (extends `AbstractUser`) in `users/models.py`
- Always reference via `settings.AUTH_USER_MODEL`, never `User` directly
- User attributes: `course` (COURSE_CHOICES), `year` (YEAR_CHOICES)
- Custom signup form: `CustomUserCreationForm` in `users/forms.py`

### App Structure
- **users**: Authentication, signup/login/logout (`users/urls.py`, `users/views.py`)
- **resources**: Document management, study groups, messaging
  - Models: `Document`, `StudyGroup`, `Message`, `GroupChat` (`resources/models.py`)
  - Forms: `DocumentUploadForm`, `StudyGroupForm`, `MessageForm` (`resources/forms.py`)

### Template Organization
- Root-level `templates/` directory (configured in `settings.TEMPLATES`)
- Modern base template: `templates/base.html` with navigation, CSS variables, and utility classes
- Shared templates: `templates/home.html` with feature cards
- App-specific: `templates/users/`, `templates/resources/`
- Auth templates extend `base.html` directly (users/base.html is just an alias)
- Empty `static/` folder (all CSS inline in templates for easy iteration)

### Media Handling
- Document uploads: `media/documents/` (set via `Document.file` field)
- Max file size: 10MB (validated in `DocumentUploadForm.clean_file()`)
- Settings: `MEDIA_URL = '/media/'`, `MEDIA_ROOT = BASE_DIR / "media"`

## Real-Time Features & External Services

### Pusher Integration (Group Chat)
- **Primary real-time solution**: Pusher handles all group chat functionality
- Real-time messaging implementation:
  - Frontend: `resources/templates/resources/group_chat.html` uses Pusher JS SDK
  - Backend: `resources/views.py::send_message()` handles AJAX POST and triggers Pusher events
  - Page render: `resources/views.py::group_chat_view()` passes Pusher credentials to template
- Pusher events: `'new-message'` on channel `f'group-{group.id}'`
- Environment variables (via `.env`): `PUSHER_APP_ID`, `PUSHER_KEY`, `PUSHER_SECRET`, `PUSHER_CLUSTER`
- Pusher client initialized at module level: `pusher_client = pusher.Pusher(...)`

### Message Flow
1. User types message in chat UI
2. JavaScript sends AJAX POST to `/resources/groups/<group_id>/send/`
3. Backend saves message to database and triggers Pusher event
4. Message immediately appears in sender's UI (no wait for Pusher)
5. Pusher broadcasts to all other connected clients
6. Other clients receive and display message in real-time

### Stream Chat (Legacy)
- Stream API still configured but NOT actively used: `STREAM_API_KEY`, `STREAM_API_SECRET`
- Token endpoint exists: `resources/views.py::get_chat_token()` (can be removed)
- **Note**: System now uses Pusher exclusively for consistency

### Commented-Out Channels/Redis
- `settings.py` contains commented-out ASGI/Redis channel layer config
- Currently using WSGI (`WSGI_APPLICATION = 'academic_assistant.wsgi.application'`)
- If adding WebSockets, uncomment `ASGI_APPLICATION` and `CHANNEL_LAYERS` blocks

## Data Model Relationships

### Study Groups
- `StudyGroup` has `creator` (ForeignKey), `members` (ManyToMany) to `CustomUser`
- Documents can be linked to groups: `Document.group` (ForeignKey to `StudyGroup`)
- Messages belong to groups: `Message.group` (ForeignKey with `related_name='messages'`)

### Document Model
- `Document.course` is CharField (NOT ForeignKey to `Course` model despite `Course` existing)
- Tags: `Document.tags` (ManyToMany to `Tag`)
- Uploaded by: `Document.uploaded_by` (ForeignKey to `AUTH_USER_MODEL`)

## Development Workflow

### Running the Server
```powershell
python manage.py runserver
```

### Database Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Creating Superuser
```powershell
python manage.py createsuperuser
```

### Dependencies
- Install: `pip install -r requirements.txt`
- Key packages: `Django==6.0`, `pusher==3.3.3`, `stream-chat==4.28.0`, `python-dotenv==1.2.1`, `pillow==12.0.0`

### Environment Setup
- Create `.env` file at project root (see `.env.example` for template)
- Required for real-time chat:
  - `PUSHER_APP_ID`, `PUSHER_KEY`, `PUSHER_SECRET`, `PUSHER_CLUSTER`
- Optional (legacy, not used):
  - `STREAM_API_KEY`, `STREAM_API_SECRET`
- Settings loads via `load_dotenv()` in `academic_assistant/settings.py`
- Get Pusher credentials at https://pusher.com

## Coding Conventions

### UI/UX Patterns
- All templates use light-blue color scheme with CSS variables (--primary-blue, --light-blue, etc.)
- Card-based layouts with rounded corners (border-radius: 12-16px) and subtle shadows
- Consistent button styles: `.btn`, `.btn-primary`, `.btn-outline`
- Form inputs have 2px borders that change to blue on focus with subtle shadow
- Responsive design with mobile breakpoints at 768px and 968px
- Animation on interactions (hover, focus, message appearance)

### View Patterns
- All resource views use `@login_required` decorator (except `view_documents`)
- Redirect patterns: `LOGIN_REDIRECT_URL = '/'`, `LOGOUT_REDIRECT_URL = '/users/login/'`
- Success messages: Use `messages.success(request, "...")` from `django.contrib`

### URL Naming
- Study group detail: `'group_detail'` (path: `groups/<int:group_id>/detail/`)
- Study group chat: `'group_chat'` (path: `groups/<int:group_id>/chat/`)
- Distinction matters: detail shows group info, chat is Messenger-style interface

### Form Handling
- Forms in `resources/forms.py` and `users/forms.py`
- Pattern: `form.save(commit=False)` → set additional fields → `form.save()`
- For ManyToMany after commit=False: call `form.save_m2m()`
- Templates iterate over form fields for custom styling

### Database
- SQLite database: `db.sqlite3` at project root
- No production database config (uses default SQLite)

## Common Tasks

### Adding New Models
1. Define in `resources/models.py` or create new app
2. Run `python manage.py makemigrations`
3. Review migration file in `migrations/`
4. Run `python manage.py migrate`

### Adding New Views
1. Define in `resources/views.py` or `users/views.py`
2. Add URL pattern to respective `urls.py`
3. Create template in `templates/resources/` or `templates/users/`
4. Apply `@login_required` if authentication needed

### Working with Documents
- Upload form: `DocumentUploadForm` includes `title`, `file`, `course`, `tags`, `group`
- Course is free text, not dropdown (despite `Course` model existing)
- Filter by course: `view_documents()` accepts `?course=<course_id>` query param (but `Document.course` is CharField—logic mismatch)

## Known Quirks
- `Document.course` is CharField, but `Course` model exists separately—inconsistent design
- `GroupChat` model defined but not actively used in views (only `StudyGroup.messages`)
- Both Pusher and Stream Chat configured—redundant real-time solutions
- `consumer.py` exists in `resources/` but unused (likely for channels/WebSockets)
- No static files currently (empty `static/` folder)
