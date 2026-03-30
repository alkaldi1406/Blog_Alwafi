from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from .models import Profile



attrs = {'class':'form-control'}

class UserLoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(attrs=attrs))
    password = forms.CharField(widget=forms.PasswordInput(attrs=attrs),label=_('Password'))


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs=attrs),label=_('First Name'))
    last_name = forms.CharField(widget=forms.TextInput(attrs=attrs),label=_('Last Name'))
    username = forms.CharField(widget=forms.TextInput(attrs=attrs),label=_('Username'))
    email = forms.EmailField(widget=forms.EmailInput(attrs=attrs),label=_('Email'))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs),label=_('Password'),strip=False,)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs),label=_('Password Confirmation'),strip=False,)



    class Meta(UserCreationForm.Meta):
        fields = ('first_name', 'last_name', 'username', 'email')





class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'bio']
