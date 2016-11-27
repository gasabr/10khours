import httplib2
from django.conf import settings
from django.shortcuts import render
import pickle
from apiclient import discovery
from .models import CalendarModel
from .forms import ChoiceForm
from gauth.models import CredentialsModel
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from oauth2client.contrib import xsrfutil

from . import handler


@login_required
def viz(request):
    """
    view which will handle plotting
    """
    h = handler.Handler(request.user.username)
    summaries = h.get_calendars_summary()
    f = 'oops'  
    form = ChoiceForm(request.GET or None, calendars_list=summaries)
    if form.is_valid():
        f = h.create_graphs([form.cleaned_data['calendar']], [form.cleaned_data['period']])
        return render(request, 'viz/viz.html', {'form': form, 'path': str(f[0])})
    
    return render(request, 'viz/viz.html', {'form': form, 'path': f})
