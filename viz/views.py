import httplib2
from django.conf import settings
from django.shortcuts import render
import pickle
from apiclient import discovery
from .forms import ChoiceForm
from .models import CalendarManager
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
    # h = handler.Handler(request.user.username)
    # get tuples (calendar_id, title_of_calendar)
    cm = CalendarManager()
    cm.update_calendars(request.user.username)
    summaries = cm.get_calendars_summary()
    form = ChoiceForm(request.POST or None, calendars_list=summaries)
    
    if form.is_valid():
        # if user asked for syncing events
        if form.cleaned_data['sync']:
            cm.sync_events(form.cleaned_data['calendar'])
        
        calendar = form.cleaned_data['calendar']
        if calendar == 'primary':
            calendar = request.user.email

        keywords_ = []
        if form.cleaned_data['keywords']:
            keywords_ = form.cleaned_data['keywords'].split(',')
            # return hm

        h = handler.Handler(request.user.username)
        images = h.create_graphs([calendar], 
                                 [form.cleaned_data['period']],
                                 keywords_,                                 
                                )
                            
        return render(request, 'viz/viz.html', {'form'  : form, 
                                                'images': images,
                                               })
    
    return render(request, 'viz/viz.html', {'form': form})
