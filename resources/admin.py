from django.contrib import admin
from .models import (
    GroupChat, StudyGroup, GroupInvite, Document, Course, Tag, Message,
    Friendship, PrivateChat, PrivateMessage, MessageReaction, MessageAttachment
)

# Register your models here.
admin.site.register(StudyGroup)
admin.site.register(GroupChat)
admin.site.register(GroupInvite)
admin.site.register(Document)
admin.site.register(Course)
admin.site.register(Tag)
admin.site.register(Message)
admin.site.register(Friendship)
admin.site.register(PrivateChat)
admin.site.register(PrivateMessage)
admin.site.register(MessageReaction)
admin.site.register(MessageAttachment)