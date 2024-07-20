from django import forms
from .models import *

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['fname', 'file_content']

class UserCreationForm(forms.ModelForm):
    class Meta:
        model = Techie
        fields = ['email', 'name',  'password']

class UserLoginForm(forms.ModelForm):
    class Meta:
        model = Techie
        fields = ['email', 'password']