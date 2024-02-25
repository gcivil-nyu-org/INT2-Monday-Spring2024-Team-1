from django import forms
from django.contrib.auth.models import User
from .models import user

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        u = super(UserRegistrationForm, self).save(commit=False)
        u.set_password(self.cleaned_data["password"])
        if commit:
            u.save()
            user.objects.create(user=u)
        return u