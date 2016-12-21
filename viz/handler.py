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
from django.db.models import Q
from apiclient import discovery
from .models import Calendar, Event
from gauth.models import CredentialsModel
from django.contrib.auth.models import User
from functools import reduce

PERIODS = ['this_month', 'this_30_days','this_week', 'today']
# <any/few>_<PERIOD>
# <any> - one calendar
# <few> - some calendars
PERIOD_TO_TYPES = {'this_month'    : ['bar', 'sum-bar'],
                   'last_30_days'  : ['bar', 'sum-bar'],
                   'this_week'     : ['bar', 'sum-bar'],
                   'any_day'       : ['pie', 'timeline'],  
                  }
           
def check_path(username, period_type, filename):
    user_static_folder = 'graphs/'+username+'/'
    full_path  = os.path.join(settings.STATIC_ROOT, user_static_folder)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    filename = period_type + '_' + filename + '.png'
        
    if os.path.exists(full_path+filename):
        os.remove(full_path+filename)
        
    image_path = '/static/'+user_static_folder+filename 
    
    return (full_path + filename, image_path)
    
def plot(y, path_to_save, plot_type, xticks):
    """
	will plot and save the image in specified folder
    """
    plt.figure(figsize=(10,5))
    xaxis = range(1, len(y)+1) if plot_type == 'this_week' else range(len(y))
    
    if plot_type=='bar-sum':
        plt.plot(range(1, len(y)+1), y)
        plt.fill_between(range(1, len(y)+1), y, color='#eeefff')
        plt.xlim([1, len(y)])
        
    elif plot_type == 'bar':
        # left=range(1, len(y)+1)
        plt.bar(left=range(1, len(y)+1), 
                height=y, 
                width=0.6, 
                align="center"
               )
        # plt.xlim([1, len(y)+1])
        plt.axis('tight')
        x1,x2,y1,y2 = plt.axis()
        plt.axis((x1, x2, 0, max(y)+2))
        
    plt.ylabel('Hours')
    ind = range(1, len(xticks)+1)    # the x locations for the groups
    plt.xticks(ind, xticks, rotation=50)
    plt.xlabel('periods')
    plt.savefig(path_to_save, bbox_inches='tight')
    
    
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
                last_day_of_month = calendar_module.monthrange(now.year, now.month)[1]
                # next_month = now.month+1 if now.month < 12 else 1
                end = start + timedelta(days=last_day_of_month)
                # end   = datetime.combine(date(now.year, 
                #                               next_month, 
                #                               1),
                #                          datetime.min.time())
                delta = timedelta(days=1)
    
            elif period_type == 'today':
                start = datetime.combine(start, datetime.min.time())
                end   = datetime.combine(start, datetime.max.time())
                delta = timedelta(hours=1)
    
            elif period_type == 'this_week':
                start = datetime.combine(date(now.year, now.month, now.day) - timedelta(days=now.weekday()),
                                         datetime.min.time())
                # obtaining last day of the week
                end   = start + timedelta(days=7)
                
            elif period_type == 'last_30_days':
                start = datetime.combine((now - timedelta(days=30)).date(),
                                          datetime.min.time())
                end   = datetime.combine(now.date(), datetime.min.time())
                
                
            bounds = []
            tmp = start
            while tmp < end:
                bounds.append(tmp)
                tmp += delta
            bounds.append(end)
            # bounds.append(end + timedelta(days=1))
                
            P.append({'type'  : period_type,
                      'start' : start,
                      'end'   : end,
                      'delta' : delta,
                      'bounds': bounds}
                    )
        return P


    def create_graphs(self, calendars, input_periods, keywords):
        """
        takes what to show on graphs in 2 lists
        plots it with matplolib
        saves images in /static/<username> 
        """
        # get types of pictures to produce from dict above
        plotting_types = PERIOD_TO_TYPES[input_periods[0]]

        # prepare data
        # get the dict periods with special function
        periods = self.create_periods(input_periods)
        bounds  = periods[0]['bounds']
        events  = []
        
        for index, b in enumerate(bounds[:-1]):
            if keywords:
                events.append(Event.objects.filter(
                        reduce(lambda x, y: x | y, [Q(summary__contains=k) for k in keywords]),
                        start__range=[str(b), str(bounds[bounds.index(b)+1])],
                        calendar__id=calendars[0],
                    ))
            else:
                events.append(Event.objects.filter(
                        start__range=[str(b), str(bounds[bounds.index(b)+1])],
                        calendar__id=calendars[0],
                    ))
        
        # spread events in bounds
        events_distribution = [0]*(len(bounds)-1)
        for i, qs in enumerate(events):
            for ev in qs.values():
                events_distribution[i] += ev['duration']
        
        events_sum_dist = list(events_distribution[:])
        for i in range(1, len(events_distribution)):
            events_sum_dist[i] += events_sum_dist[i-1]
        
        days = [x.day for x in bounds[:-1]]
        
        path_to_save, static_path1 = check_path(self.user.username, 
                                                input_periods[0], 
                                                'bar'
                                               )
        plot(y=events_distribution,
             xticks=days,
             path_to_save=path_to_save,
             plot_type='bar'
            )
        
        images = []
        images.append({'title'  : 'This month progress by day',
                       'path'   : static_path1,
                       'summary': '',
                       })
            
        path_to_save, static_path2 = check_path(self.user.username, 
                                                input_periods[0], 
                                                'bar-sum'
                                               )
        plot(y=events_sum_dist,
             xticks=days,
             path_to_save=path_to_save,
             plot_type='bar-sum'
            )
        images.append({'title'  : 'This month progress summary',
                       'path'   : static_path2,
                       'summary': '',
                       })
        
        return images
