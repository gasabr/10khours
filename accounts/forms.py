from django import forms
from django.contrib.auth import (
    login,
    logout,
    get_user_model,
    authenticate
)

User = get_user_model()


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if not user:
                raise forms.ValidationError('this user doesnot exist')

            if not user.check_password(password):
                raise forms.ValidationError("incorrect password ")

            if not user.is_active:
                raise forms.ValidationError("user is no longer active")

        return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegistraterForm(forms.ModelForm):

    email = forms.EmailField(label='Enter email')
    password = forms.CharField(widget=forms.PasswordInput)


    class Meta:
        model = User
        fields = [
            'email',
            'password',
            # 'password2',
        ]

    def clean_email2(self):
        email = self.cleaned_data.get('email')
        email_qs = User.objects.filter(email=email)

        if email_qs.exists():
            raise forms.ValidationError("This email has already been used")

        return email
