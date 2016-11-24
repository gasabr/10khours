from django.contrib.auth import (
	login,
	logout,
	get_user_model,
	authenticate
)
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm, UserRegistraterForm


def login_view(request):
	print(request.user.is_authenticated())
	title = 'Login'
	form = UserLoginForm(request.POST or None)
	if form.is_valid():
		username = form.cleaned_data.get('username')
		password = form.cleaned_data.get('password')

		user = authenticate(username=username, password=password)
		login(request, user)

	return render(request, "accounts/form.html", {"form": form, "title": title})


def logout_view(request):
	logout(request)
	return render(request, "accounts/form.html", {})


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
		password = form.cleaned_data.get('password')
		user.set_password(password)
		user.save()
		return redirect('get_creds') # to the 1st step of OAuth2

	return render(request, "accounts/form.html", context)
