from django import forms
from .models import Document
from .models import StudyGroup
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type your message...'})
        }

class StudyGroupForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = ['name', 'description']

class DocumentUploadForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=StudyGroup.objects.all(), required=False, empty_label="No group")

    class Meta:
        model = Document
        fields = ['title', 'file', 'course', 'tags', 'group']
        widgets = {
            'course': forms.TextInput(attrs={'placeholder': 'Enter course name'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file.size > 10 * 1024 * 1024:  # 10MB max
            raise forms.ValidationError("File too large. Max size is 10MB.")
        return file