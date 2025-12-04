# Quick Setup Guide for Real-Time Chat

This guide will help you get the real-time chat feature working in your Academic Assistant application.

## Step 1: Get Pusher Credentials

1. Visit https://pusher.com and sign up for a free account
2. Create a new Channels app
3. From your app dashboard, copy the following:
   - App ID
   - Key
   - Secret
   - Cluster

## Step 2: Configure Environment Variables

1. In the project root, copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and fill in your Pusher credentials:
   ```env
   PUSHER_APP_ID=123456
   PUSHER_KEY=abc123def456
   PUSHER_SECRET=xyz789uvw012
   PUSHER_CLUSTER=us2
   ```

## Step 3: Verify Installation

1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Step 4: Test the Chat

1. Create or login to a user account
2. Create a study group or join an existing one
3. Navigate to the group chat (click "Chat" in the group detail page)
4. Send a test message

### Testing Real-Time Updates (Two Users)

To fully test real-time functionality:

1. **Open two browser windows/tabs:**
   - Window 1: Login as User A
   - Window 2: Login as User B (use incognito/private mode)

2. **Both users join the same study group**

3. **Both users open the group chat:**
   - Navigate to `/resources/groups/{group_id}/chat/`

4. **Send messages from each user:**
   - User A sends a message → should appear immediately in both windows
   - User B sends a message → should appear immediately in both windows

## Troubleshooting

### Messages Not Appearing

**Check Browser Console (F12):**
- Look for Pusher connection errors
- Check for JavaScript errors

**Common Issues:**

1. **"Pusher is not defined"**
   - Solution: Ensure Pusher script is loading (check internet connection)

2. **"Failed to fetch"**
   - Solution: Django server must be running
   - Check CSRF token is present

3. **No real-time updates**
   - Solution: Verify Pusher credentials in `.env`
   - Restart Django server after changing `.env`
   - Check Pusher dashboard for connection activity

4. **Messages send but don't appear**
   - Solution: Check browser console for errors
   - Verify channel name matches: `group-{group_id}`
   - Check Pusher event name: `new-message`

### Pusher Dashboard

Monitor real-time activity:
1. Login to Pusher dashboard
2. Select your app
3. Go to "Debug Console"
4. Watch for:
   - Connection events
   - Channel subscriptions
   - Message triggers

## Features Implemented

✅ **Immediate Message Display**
- Sender sees their message instantly (optimistic UI)
- No page refresh needed

✅ **Real-Time Broadcasting**
- All connected users receive messages in real-time
- Uses Pusher WebSocket channels

✅ **Modern UI**
- WhatsApp-style chat interface
- Green bubbles for own messages
- White bubbles for other users' messages
- Timestamps on all messages
- Auto-scroll to latest message

✅ **Robust Backend**
- AJAX message sending
- Message validation (max 5000 characters)
- Member verification
- Database persistence

## API Endpoints

### View Chat Page
- **URL**: `/resources/groups/{group_id}/chat/`
- **Method**: GET
- **Auth**: Required
- **Response**: Renders chat HTML with existing messages

### Send Message
- **URL**: `/resources/groups/{group_id}/send/`
- **Method**: POST
- **Auth**: Required
- **Body**: `content=message_text`
- **Response**: JSON with success status and timestamp

Example AJAX call:
```javascript
fetch("/resources/groups/1/send/", {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-CSRFToken': csrfToken
  },
  body: `content=${encodeURIComponent(message)}`
})
```

## Architecture

### Message Flow

```
User A Types Message
       ↓
  AJAX POST to Backend
       ↓
Backend Saves to Database
       ↓
Backend Triggers Pusher Event
       ↓
    ┌──────────┴──────────┐
    ↓                     ↓
User A (Immediate)   User B (Real-time)
 Shows Message       Receives via Pusher
```

### Components

1. **Frontend (group_chat.html)**
   - Pusher JS SDK
   - AJAX message sending
   - Real-time message receiving
   - UI rendering

2. **Backend (views.py)**
   - `group_chat_view()`: Render page
   - `send_message()`: Handle AJAX, save, trigger Pusher

3. **Pusher**
   - Channel: `group-{group_id}`
   - Event: `new-message`
   - Payload: username, message, timestamp

## Next Steps

### Recommended Enhancements

1. **Typing Indicators**
   - Show when users are typing

2. **Read Receipts**
   - Track message read status

3. **File Sharing**
   - Send images/documents in chat

4. **Message Editing/Deletion**
   - Edit or delete sent messages

5. **Emoji Support**
   - Add emoji picker

6. **Notifications**
   - Browser notifications for new messages

7. **Message Search**
   - Search chat history

## Support

For issues or questions:
1. Check this guide
2. Review browser console errors
3. Check Pusher dashboard
4. Review Django server logs
5. Open a GitHub issue

## Useful Commands

```bash
# Run server
python manage.py runserver

# Check for errors
python manage.py check

# View logs (terminal where server is running)

# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```
