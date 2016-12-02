from django.contrib.auth import (
	login,
	logout,
	get_user_model,
	authenticate
)
import httplib2
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from gauth.models import CredentialsModel
from .forms import UserLoginForm, UserRegistraterForm
from oauth2client.client import HttpAccessTokenRefreshError


def login_view(request):
	print(request.user.is_authenticated())
	title = 'Login and check credentials'
	form = UserLoginForm(request.POST or None)
	if form.is_valid():
		email    = form.cleaned_data.get('email')
		password = form.cleaned_data.get('password')

		user = get_user_model().objects.get(email=email)
		login(request, user)

		try:
			creds = CredentialsModel.objects.get(id__email=email).credentials
		except CredentialsModel.DoesNotExist as e:
			# if creds were deleted or died
			return redirect('get_creds')

        # TODO: change this to proprietary statement
		if creds.access_token_expired:
			try:
				creds.refresh(httplib2.Http())
				return redirect('viz')
			except HttpAccessTokenRefreshError as e:
				return redirect('get_creds')
			else:
				return redirect('get_creds')
		else:
		    redirect('viz')

	return render(request, "accounts/form.html", {"form": form, "title": title})


@login_required
def logout_view(request):
	logout(request)
	return redirect('login')


def register_view(request):
	title = "Registration"
	form = UserRegistraterForm(request.POST or None)
	context = {
		'title' : title,
		'form' : form
	}

	if form.is_valid():
		print("form is valid")
		user = form.save(commit=False)
		username_from_email = form.cleaned_data.get('email').split('@')[0]
		password = form.cleaned_data.get('password')
		
		user.username = username_from_email
		user.set_password(password)
		user.save()
		return redirect('get_creds') # to the 1st step of OAuth2

	return render(request, "accounts/form.html", context)
