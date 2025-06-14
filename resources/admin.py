from django.contrib import admin
from .models import GroupChat
# Register your models here.
from .models import StudyGroup

admin.site.register(StudyGroup)



admin.site.register(GroupChat)