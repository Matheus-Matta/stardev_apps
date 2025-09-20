# account/forms_thumbnail.py
from django import forms
from core.models import Files

class FilesForm(forms.ModelForm):
    class Meta:
        model = Files
        fields = ["file"]