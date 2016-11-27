from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.template.context import RequestContext
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User, UserManager
from django.shortcuts import render_to_response, redirect, render
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)

# to get credentials
from .models import CredentialsModel

import pickle
from YamJam import yamjam
from apiclient import discovery
from django.conf import settings
from oauth2client.contrib import xsrfutil
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.contrib.django_util.storage import DjangoORMStorage


def get_flow(request):    
    flow = OAuth2WebServerFlow(
        client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        scope='https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/calendar',
        redirect_uri='http://10khours.ru/oauth2/redirect/',
        access_type='offline',
    )

    return flow


def home(request):
   context = RequestContext(request,
                           {'request': request,
                            'user': request.user})
   return render_to_response('gauth/home.html',
                             context=context)


def get_creds(request):
    flow = get_flow(request)
    flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                       request.user.id)
    request.session['flow'] = pickle.dumps(flow).decode('iso-8859-1')
    redirect_uri = flow.step1_get_authorize_url()

    return redirect(redirect_uri)


def oauth2redirect(request):
    print("oauth2redirect")
    # Make sure that the request is from who we think it is
    if not xsrfutil.validate_token(settings.SECRET_KEY,
                                   request.GET.get('state').encode('utf8'),
                                   request.user.id):
        return HttpResponseBadRequest()
    print("user ID = ", request.user.id)

    code = request.GET.get('code')
    error = request.GET.get('error')

    if code:
        flow = get_flow(request)
        credentials = flow.step2_exchange(code)

        request.session['creds'] = credentials.to_json()
        email = credentials.id_token.get("email")
        user = User.objects.get(email=email)

        # Since we've oauth2'd the user, we should set the backend appropriately
        # This is usually done by the authenticate() method.
        user.backend = 'django.contrib.auth.backends.ModelBackend'

        # Refresh token is needed for renewing google api access token
        if credentials.refresh_token:
            user.refresh_token = credentials.refresh_token
        user.save()

        storage = DjangoORMStorage(CredentialsModel, 'id', user, 'credentials')
        storage.put(credentials)

        # Register that the user has successfully logged in
        auth_login(request, user)

        return redirect('viz')

    elif code is None and error:
        return HttpResponse(str(error))
    else:
        return HttpResponseBadRequest()

