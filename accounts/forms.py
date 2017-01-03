from django import forms
from django.contrib.auth import (
    login,
    logout,
    get_user_model,
    authenticate
)
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class UserLoginForm(forms.Form):
    email    = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='password')


    def clean_email(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email:
            try:
                username = User.objects.get(email=email).username
                user     = authenticate(username=username, password=password)

            except User.DoesNotExist as e:
                raise forms.ValidationError(_("There's no user with such email"))

        return email


    def clean_password(self):
        email    = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            username = User.objects.get(email=email).username
            user = authenticate(username=username, password=password)

            if user is None:
                raise forms.ValidationError(_("Incorrect password."))

            if not user.check_password(password):
                raise forms.ValidationError(_("Incorrect password."))

        return password


    def clean(self, *args, **kwargs):
        email    = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

    class Meta:
        model = User
        fields = [
            'email',
            'password',
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError(_("User with such email already exists."))

        email_domain = email.split('@')[1]
        if email_domain != 'gmail.com':
            raise forms.ValidationError(_("Please, enter your gmail address"))

        return email
