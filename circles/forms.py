from django import forms

from .models import FamilyCircle


class CircleForm(forms.ModelForm):
    class Meta:
        model = FamilyCircle
        fields = ['circle_name']
        labels = {'circle_name': 'Circle name'}
        help_texts = {'circle_name': 'Example: The Sanchez Family'}

    def clean_circle_name(self):
        name = self.cleaned_data['circle_name'].strip()
        if len(name) < 3:
            raise forms.ValidationError('Circle name must be at least 3 characters.')
        return name