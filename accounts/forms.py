from django import forms

from .models import CustomUser


class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'role']
        labels = {'role': 'Register as'}
        help_texts = {'username': 'Letters, numbers and @ . + - _ only.'}

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get('password1')
        password2 = cleaned.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Passwords do not match.')
        elif password1 and len(password1) < 8:
            self.add_error('password1', 'Password must be at least 8 characters.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])  # hashes the password
        if commit:
            user.save()
        return user