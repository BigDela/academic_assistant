# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Document, Course
from django.contrib.auth.decorators import login_required
from .models import StudyGroup
from .forms import StudyGroupForm
from django.contrib import messages
from .forms import MessageForm
from .models import GroupChat
from .forms import DocumentUploadForm
from django.conf import settings
from django.views.decorators.http import require_POST



@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            form.save_m2m()
            return redirect('view_documents')  # or wherever you want to redirect after upload
    else:
        form = DocumentUploadForm()

    return render(request, 'resources/upload.html', {'form': form})

def view_documents(request):
    course_id = request.GET.get('course')
    courses = Course.objects.all()
    documents = Document.objects.all()
    if course_id:
        documents = documents.filter(course__id=course_id)
    return render(request, 'resources/view.html', {'documents': documents, 'courses': courses})



@login_required
def create_study_group(request):
    if request.method == 'POST':
        form = StudyGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            group.members.add(request.user)
            messages.success(request, "Study group created successfully!")
            return redirect('group_list')
    else:
        form = StudyGroupForm()
    return render(request, 'resources/create_group.html', {'form': form})

@login_required
def group_list(request):
    groups = StudyGroup.objects.all()
    return render(request, 'resources/group_list.html', {'groups': groups})
@login_required
def group_detail(request, group_id):
    group = get_object_or_404(StudyGroup, id=group_id)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.group = group
            message.user = request.user
            message.save()
            return redirect('group_detail', group_id=group.id)
    else:
        form = MessageForm()

    messages = group.messages.all()

    return render(request, 'resources/group_detail.html', {
        'group': group,
        'messages': messages,
        'form': form
    })
@login_required
def join_group(request, group_id):
    group = get_object_or_404(StudyGroup, id=group_id)
    if request.user not in group.members.all():
        group.members.add(request.user)
        messages.success(request, "You joined the group!")
    else:
        messages.info(request, "You are already a member of this group.")
    return redirect('group_detail', group_id=group.id)


import pusher

pusher_client = pusher.Pusher(
    app_id=settings.PUSHER_APP_ID,
    key=settings.PUSHER_KEY,
    secret=settings.PUSHER_SECRET,
    cluster=settings.PUSHER_CLUSTER,
    ssl=True
)

@login_required
def group_chat_view(request, group_id):
    """Render the chat page with existing messages."""
    group = get_object_or_404(StudyGroup, id=group_id)
    messages_qs = group.messages.all().order_by('timestamp')
    documents = group.documents.all()

    return render(request, 'resources/group_chat.html', {
        'group': group,
        'messages': messages_qs,
        'documents': documents,
        'pusher_key': settings.PUSHER_KEY,
        'pusher_cluster': settings.PUSHER_CLUSTER,
    })


@login_required
@require_POST
def send_message(request, group_id):
    """Handle AJAX message sending and trigger Pusher event."""
    group = get_object_or_404(StudyGroup, id=group_id)
    
    # Verify user is a member
    if request.user not in group.members.all():
        return JsonResponse({'success': False, 'error': 'You are not a member of this group'}, status=403)
    
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'success': False, 'error': 'Message content cannot be empty'}, status=400)
    
    if len(content) > 5000:
        return JsonResponse({'success': False, 'error': 'Message too long (max 5000 characters)'}, status=400)
    
    # Create and save message
    from .models import Message
    message = Message.objects.create(
        group=group,
        user=request.user,
        content=content
    )
    
    # Trigger Pusher event for real-time updates to other users
    pusher_client.trigger(f'group-{group.id}', 'new-message', {
        'username': request.user.username,
        'message': message.content,
        'timestamp': message.timestamp.isoformat(),
        'message_id': message.id,
    })
    
    return JsonResponse({
        'success': True,
        'message_id': message.id,
        'timestamp': message.timestamp.isoformat(),
    })


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@login_required
@require_POST
@csrf_exempt
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, user=request.user)

    group_id = message.group.id
    message.delete()

    # Notify via Pusher
    pusher_client.trigger(f'group-{group_id}', 'delete-message', {
        'message_id': message_id
    })

    return JsonResponse({'status': 'success'})


from django.http import JsonResponse
from stream_chat import StreamChat
from django.conf import settings
from django.contrib.auth.decorators import login_required

@login_required
def get_chat_token(request):
    client = StreamChat(api_key=settings.STREAM_API_KEY, api_secret=settings.STREAM_API_SECRET)
    user_id = str(request.user.id)
    client.upsert_user({"id": user_id, "name": request.user.username})
    token = client.create_token(user_id)
    return JsonResponse({"token": token, "user_id": user_id, "api_key": settings.STREAM_API_KEY})
