from django import forms
from .models import Testimonial


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['client_name', 'service', 'rating', 'body', 'client_photo']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} star{"s" if i > 1 else ""}') for i in range(1, 6)]),
            'body': forms.Textarea(attrs={'rows': 4, 'maxlength': 800}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['client_name'].initial = user.get_full_name()
            self.fields['client_name'].widget.attrs['readonly'] = True
