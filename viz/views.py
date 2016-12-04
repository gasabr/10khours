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
    view with visualization of the data
    """
    # on creation will check current list of calendars and refresh it if needed
    h = handler.Handler(request.user.username)
    # get tuples (calendar_id, title_of_calendar)
    summaries = h.get_calendars_summary()
    f = 'oops'
    form = ChoiceForm(request.GET or None, calendars_list=summaries)
    if form.is_valid():
        images = h.create_graphs([form.cleaned_data['calendar']], 
                                 [form.cleaned_data['period']])
        e = "your token expires in "+str(h.get_access_token().expires_in)+" sec."
        # return a
                            
        return render(request, 'viz/viz.html', {'form'  : form, 
                                                'images': images,
                                                'expires_in': e})
    
    return render(request, 'viz/viz.html', {'form'   : form, 'path' : f})
