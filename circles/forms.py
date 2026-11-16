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


class JoinCircleForm(forms.Form):
    invite_code = forms.CharField(
        max_length=20,
        label='Invite code',
        help_text='Ask your family administrator for the 8-character code.',
    )

    def clean_invite_code(self):
        code = self.cleaned_data['invite_code'].strip().upper()
        if len(code) != 8 or not code.isalnum():
            raise forms.ValidationError('An invite code has exactly 8 letters and numbers.')
        return code