from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from .validators import validate_email,validate_username
from django import forms
class NewUserForm(UserCreationForm):
	username = forms.CharField(max_length=100,validators=[validate_username],
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'class': 'form-control',
                                                             }))
	email = forms.EmailField(required=True,validators = [validate_email],
                             widget=forms.TextInput(attrs={'placeholder': 'Email',
                                                           'class': 'form-control',
                                                           }))
	password1 = forms.CharField(max_length=50,
                                required=True,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                  'class': 'form-control',
                                                                  'data-toggle': 'password',
                                                                  'id': 'password',
                                                                  }))
	password2 = forms.CharField(max_length=50,
                                required=True,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password',
                                                                  'class': 'form-control',
                                                                  'data-toggle': 'password',
                                                                  'id': 'password',
                                                                  'label':'Confirm Password',
                                                                  }))
	class Meta:
        
		model = User
		fields = ['username', 'email', 'password1', 'password2']
	
	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user 
	
class AuthenticationForm(AuthenticationForm):
	username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'class': 'form-control',
                                                             }))
	password = forms.CharField(max_length=50,
                               required=True,
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'form-control',
                                                                 'data-toggle': 'password',
                                                                 'id': 'password',
                                                                 'name': 'password',
                                                                 }))
	
	
	class Meta:
		model = User
		fields = ['username', 'password']


class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Email',
                                                           'class': 'form-control',
                                                           }))
    subject = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Subject',
                                                           'class': 'form-control',
                                                           }))
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Type in your message',
                                                           'class': 'form-control',
                                                           }), required=True)