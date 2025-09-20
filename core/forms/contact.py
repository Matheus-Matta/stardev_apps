# account/forms_contact.py
from django import forms
from core.models import Contact

class ContactForm(forms.ModelForm):
    """
    Contact:
    - não permite editar 'account'
    - 'value' pode ser e-mail/telefone; validações específicas podem ser adicionadas conforme type
    """
    class Meta:
        model = Contact
        fields = ["type", "value", "is_verified"]
