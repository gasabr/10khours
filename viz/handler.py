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
from .models import CalendarModel
from gauth.models import CredentialsModel
from django.contrib.auth.models import User

PERIODS = ['this_month', 'this_week', 'today']


def get_duration(event):
    """
    event is { 'start': {'dataTime' : datetime.datetime(),},
               'end': {'dataTime' : datetime.datetime(),},
               ...
    returns difference in hours
    """
    end = datetime.strptime(event['end']['dateTime'], '%Y-%m-%dT%H:%M:%S+03:00')
    start = datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S+03:00')
    return float((end-start).seconds / 60) / 60

class Handler():
    """
    Class to handle all operations on viz view (@viz/views.py) such that:
      - getting credentials from username, checking expiration time
      - getting list of calendars from Google Api, updating CalendarsModel
      - plotting data, saving graphs
    """
    def __init__(self, username):
        """
        builds user, credential, service
        """
        self.user = User.objects.get(username=username)

        # get creds from db, TODO: check should be separate function
        self.creds = CredentialsModel.objects.get(id__username=username).credentials
        if self.creds.access_token_expired:
            # check time instead of expiration check
            print("oops")

        # build service to get access to API
        self.http = self.creds.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=self.http)

        # calendars in list of dictionaries
        current_calendars = self.service.calendarList().list().execute().get('items', [])   

        # if there are new calendars add them to db
        for c in current_calendars:
            try:
                CalendarModel.objects.filter(id=c['id'])
            except CalendarModel.DoesNotExist:
                new_cm = CalendarModel.objects.create(id=c['id'], 
                                                      user=user, 
                                                      name=c['summary'])                                      
                new_cm.save()
    
          
    def get_access_token(self):
        return self.creds.get_access_token()
        
        
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
    

    def fetch_events(self, calendars_ids, periods):
        """
        takes array of calendars ids and time interval
        returns {'calendar_id': [events,...,]}
        """
        events = []
        for c_id in calendars_ids:
            for period in periods:
                timeMax = period['end'].isoformat()+'Z'
                timeMin = period['start'].isoformat()+'Z'
                items   = self.service.events().list(calendarId=c_id,
                                                     timeMax=timeMax,
                                                     timeMin=timeMin
                                                    ).execute().get('items', [])
                                                  
                events.append({'calendarId' : c_id,
                               'period_type': period['type'],
                               'items'      : items}
                            )

        return events
        
    
    def spread_events(self, events, periods):
        X = []
        for e in events:
            e['items_in_periods'] = {}
            bounds, delta = self.get_bounds(periods, e['period_type'])
            # X = [map(str, x) for x in bounds]
            for i in e['items']:
                period_start = bounds[0]
                event_start = datetime.strptime(i['start']['dateTime'], '%Y-%m-%dT%H:%M:%S+03:00')
                while period_start < event_start:
                    period_start += delta
                i[e['period_type']] = period_start
                
        return events


    def get_calendars_summary(self):
        """
        returns [(id, name), ...,] for each calendar in db for given user
        """
        return [(x.id, x.name) for x in CalendarModel.objects.all().filter(user__username=self.user.username)]


    def create_graphs(self, calendars, periods):
        """
        takes what to show on graphs in 2 lists
        plots it with matplolib
        saves images in /BASE_DIR/<username> 
        """
        if self.token_need_renovation():
            h = self.creds.authorize(httplib2.Http())
            self.creds.refresh(self.http)
        # prepare data
        P = self.create_periods(periods)
        events_series = self.spread_events(self.fetch_events(calendars, P), P)
        
        # create folder to store images
        user_static_folder = 'graphs/'+self.user.username+'/'
        full_path  = os.path.join(settings.STATIC_ROOT, user_static_folder)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        file_name = 'bar.png'
        
        if os.path.exists(full_path+file_name):
            os.remove(full_path+file_name)
        
        tmp_period = periods[0]
        D = []
        for index, bound in enumerate(P[0]['bounds']):
            if index >= len(D):
                D.append(0)
            for e in events_series[0]['items']:
                if e[P[0]['type']] == bound:
                    D[index] += get_duration(e)
                    
        image_path = '/static/'+user_static_folder+file_name    
            
        plt.bar([l for l, _ in enumerate(D)], height=D)
        plt.grid(True)
        plt.savefig(full_path+file_name)
        plt.clf()

        return [image_path]

