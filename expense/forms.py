from django.forms import ModelForm, widgets
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import *

class CreateUserForm(UserCreationForm):
	group = forms.CharField()
	class Meta:
		model = User
		fields = UserCreationForm.Meta.fields + ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'group')

