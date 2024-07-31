from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['fname', 'file_content']

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = Techie
        fields = ['name', 'email', 'avatar', 'user_plan', 'password1', 'password2']
