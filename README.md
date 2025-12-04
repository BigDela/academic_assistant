# Academic Assistant

A Django-based academic resource-sharing platform that enables students to upload documents, join study groups, and participate in real-time group chats.

## Features

- **User Authentication**: Custom user model with course and year level
- **Document Management**: Upload and share academic resources (max 10MB)
- **Study Groups**: Create and join study groups with other students
- **Real-Time Chat**: Modern messaging interface powered by Pusher
- **Document Organization**: Tag and categorize documents by course

## Tech Stack

- **Backend**: Django 6.0
- **Database**: SQLite (development)
- **Real-Time**: Pusher (WebSocket service)
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Authentication**: Django built-in auth with custom user model

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Pusher account (free tier available at https://pusher.com)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/BigDela/academic_assistant.git
cd academic_assistant
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Pusher credentials:

```env
PUSHER_APP_ID=your_app_id
PUSHER_KEY=your_key
PUSHER_SECRET=your_secret
PUSHER_CLUSTER=your_cluster
```

**Get Pusher Credentials:**
1. Sign up at https://pusher.com
2. Create a new Channels app
3. Copy credentials from your dashboard

### 4. Run Database Migrations

```bash
python manage.py migrate
```

### 5. Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Visit http://localhost:8000 in your browser.

## Usage

### Creating an Account

1. Navigate to http://localhost:8000/users/signup/
2. Fill in username, email, course, and year level
3. Create a password and submit

### Uploading Documents

1. Log in to your account
2. Go to "Upload Document" (http://localhost:8000/resources/upload/)
3. Fill in document details:
   - Title
   - File (max 10MB)
   - Course name
   - Tags (optional)
   - Study group (optional)
4. Submit to upload

### Creating Study Groups

1. Navigate to "Create Study Group"
2. Enter group name and description
3. Submit to create
4. Share the group with other students

### Using Real-Time Chat

1. Join a study group
2. Click "Chat" to enter the group chat room
3. Type messages in the input field
4. Press Enter or click "Send"
5. Messages appear instantly for all group members

**Chat Features:**
- ✅ Instant message delivery
- ✅ Real-time updates across all connected users
- ✅ WhatsApp-style modern UI
- ✅ Message timestamps
- ✅ Auto-scroll to latest messages
- ✅ Visual distinction between your messages and others

## Project Structure

```
academic_assistant/
├── academic_assistant/       # Project settings
│   ├── settings.py          # Django configuration
│   ├── urls.py              # Root URL routing
│   └── wsgi.py              # WSGI entry point
├── users/                   # User authentication app
│   ├── models.py            # CustomUser model
│   ├── forms.py             # Signup forms
│   └── views.py             # Auth views
├── resources/               # Core app (documents, groups, chat)
│   ├── models.py            # Document, StudyGroup, Message models
│   ├── views.py             # Business logic
│   ├── forms.py             # Upload and message forms
│   └── templates/           # HTML templates
├── templates/               # Shared templates
├── media/                   # Uploaded files
├── static/                  # Static assets
├── db.sqlite3              # SQLite database
├── manage.py               # Django management script
└── requirements.txt        # Python dependencies
```

## Key Technologies

### Pusher Real-Time Integration

The chat system uses Pusher Channels for real-time communication:

**How It Works:**
1. User sends a message via AJAX
2. Backend saves to database and triggers Pusher event
3. Pusher broadcasts to all connected clients
4. Frontend receives event and displays message
5. Sender sees message immediately (optimistic UI)

**Configuration:**
- Pusher credentials in `.env`
- Client initialized in `resources/views.py`
- Frontend subscribes to channel `group-{group_id}`
- Events: `new-message`, `delete-message`

## Development

### Running Tests

```bash
python manage.py test
```

### Making Database Changes

1. Modify models in `models.py`
2. Create migration:
   ```bash
   python manage.py makemigrations
   ```
3. Apply migration:
   ```bash
   python manage.py migrate
   ```

### Admin Panel

Access Django admin at http://localhost:8000/admin/

## Troubleshooting

### Chat Not Working

**Issue**: Messages don't appear in real-time

**Solutions:**
1. Verify `.env` file exists with correct Pusher credentials
2. Check browser console for JavaScript errors
3. Ensure Pusher app is active in dashboard
4. Verify network connectivity to Pusher servers

### File Upload Errors

**Issue**: Document upload fails

**Solutions:**
1. Check file size (max 10MB)
2. Verify `media/` directory exists and is writable
3. Ensure `MEDIA_ROOT` is configured in settings

### Database Errors

**Issue**: Migration or model errors

**Solutions:**
1. Delete `db.sqlite3` (warning: loses data)
2. Delete migration files (keep `__init__.py`)
3. Run `python manage.py makemigrations`
4. Run `python manage.py migrate`

## Known Issues

- `Document.course` is CharField but `Course` model exists (inconsistency)
- `GroupChat` model defined but unused
- Stream Chat configured but not actively used

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for educational purposes.

## Contact

For questions or issues, please open an issue on GitHub.
