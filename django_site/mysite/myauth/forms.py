from django import forms
from django.core import validators
from django.contrib.auth.models import (Group, User)

from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = "bio", "avatar"
