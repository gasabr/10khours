from django.contrib.auth import (
	login,
	logout,
	get_user_model,
	authenticate
)
from django.db import IntegrityError
import httplib2
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from gauth.models import CredentialsModel
from .forms import UserLoginForm, UserRegistrationForm
from oauth2client.client import HttpAccessTokenRefreshError
from django import forms


def login_view(request):
	title  = 'Log in'
	button = 'log in'
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
	return render(request, "accounts/form.html", {"form"  : form, 
	                                              "title" : title,
	                                              "button": button,
	                                              })


@login_required
def logout_view(request):
	logout(request)
	return redirect('home')


def register_view(request):
	form = UserRegistrationForm(request.POST or None)

	context = {
		'title' : "Registration",
		'form'  : form,
		'button': "sign up",
	}

	if form.is_valid():
		user = form.save(commit=False)
		email = form.cleaned_data.get('email')
		username_from_email = form.cleaned_data.get('email').split('@')[0]
		password = form.cleaned_data.get('password')

		user.username = username_from_email
		user.email = form.cleaned_data.get('email')
		user.set_password(password)
		user.save()
		return redirect('get_creds') # to the 1st step of OAuth2
	else:
		return render(request, "accounts/form.html", context)
