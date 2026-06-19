from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'maxlength': 2000}),
            'phone': forms.TextInput(attrs={'placeholder': '+256 700 000 000'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone and not phone.startswith('+'):
            phone = '+256' + phone.lstrip('0')
        return phone
