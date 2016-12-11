import os
import httplib2
import calendar
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta, date
import calendar as calendar_module
from django.conf import settings
from apiclient import discovery
from .models import Calendar, Event
from gauth.models import CredentialsModel
from django.contrib.auth.models import User

PERIODS = ['this_month', 'this_30_days','this_week', 'today']
# <any/few>_<PERIOD>
# <any> - one calendar
# <few> - some calendars
PERIOD_TO_GRAPH = {'any_this_month': ['bar', 'bar_sum'],
                   'any_this_week' : ['bar', 'multi_bar'],
                   'any_day'       : ['pie', 'timeline'],  
                  }
           
def check_or_create_path(username):
    user_static_folder = 'graphs/'+username+'/'
    full_path  = os.path.join(settings.STATIC_ROOT, user_static_folder)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    filename = 'bar.png'
        
    if os.path.exists(full_path+filename):
        os.remove(full_path+filename)
        
    image_path = '/static/'+user_static_folder+filename 
    
    return (full_path, filename, image_path)
    

class Handler():
    """
    Class to handle all operations on viz view (@viz/views.py) such that:
      - getting credentials from username, checking expiration time
      - getting list of calendars from Google API
      - plotting data, saving graphs
    """
    def __init__(self, username):
        """
        builds user, credential, service
        """
        self.user = User.objects.get(username=username)
        
        
    def token_need_renovation(self):
        """
        will return True if credentials.access_token.expires_in < 5 minutes
        False otherwise
        """
        expires_in = self.creds.get_access_token().expires_in
        return True if expires_in < 1200 else False
        
                
    def create_periods(self, periods):
        P = []
        now   = datetime.now()
        start = datetime.utcnow()
        end   = datetime.utcnow()
        delta = timedelta(days=1)

        for period_type in periods:
            if period_type == 'this_month':
                start = datetime.combine(date(now.year, now.month, 1), 
                                         datetime.min.time())
                # How to make it readable?
                # obtaining last day of the month
                end   = datetime.combine(date(now.year, now.month, calendar_module.monthrange(now.year, now.month)[1]),
                                         datetime.min.time())
                delta = timedelta(days=1)
    
            elif period_type == 'today':
                start = datetime.combine(start, datetime.min.time())
                end   = datetime.combine(start, datetime.max.time())
                delta = timedelta(hours=1)
    
            elif period_type == 'this_week':
                start = datetime.combine(date(now.year, now.month, now.day) - timedelta(days=now.weekday()),
                                         datetime.min.time())
                # obtaining last day of the week
                end   = start + timedelta(days=6)
                delta = timedelta(days=1)
                
            elif period_type == 'last_30_days':
                start -= timedelta(days=30)
                
                
            bounds = []
            tmp = start
            while tmp < end:
                bounds.append(tmp)
                tmp += delta
            bounds.append(end)
                
            P.append({'type'  : period_type,
                      'start' : start,
                      'end'   : end,
                      'delta' : delta,
                      'bounds': bounds}
                    )
        return P
       
                                
    def get_bounds(self, periods, period_type):
        for p in periods:
            if p['type'] == period_type:
                return (p['bounds'], p['delta'])
        return ()


    def create_graphs(self, calendars, input_periods):
        """
        takes what to show on graphs in 2 lists
        plots it with matplolib
        saves images in /static/<username> 
        """
        # prepare data
        periods = self.create_periods(input_periods)
        bounds = periods[0]['bounds']
        events = []
        for index, b in enumerate(bounds[:-1]):
            events.append(Event.objects.filter(start__range=[str(b), str(bounds[bounds.index(b)+1])],
                                               calendar__id=calendars[0]
                                              ))
        events_distribution = [0]*30
        for i, qs in enumerate(events):
            for ev in qs.values():
                events_distribution[i] += ev['duration']
        # create folder to store images
        full_path, filename, image_path = check_or_create_path(self.user.username)
            
        plt.bar(bounds, 
                height=events_distribution)
        plt.xaxis_date()
        plt.grid(True)
        plt.savefig(full_path+filename)
        plt.clf()

        return [image_path]

