import os
import httplib2
import calendar
from datetime import datetime, timedelta, date
from django.conf import settings
from apiclient import discovery
from .models import CalendarModel, PeriodModel
from gauth.models import CredentialsModel
from django.contrib.auth.models import User


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
        http = self.creds.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=http)

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
    

    def get_events(self, calendars_ids, start_time, end_time):
        """
        takes array of calendars ids and time interval
        returns {'calendar_id': [events_id,...,]}
        """
        events = {}
        for c_id in calendars_ids:
            events[c_id] = self.service.events().list(calendarId=c_id,
                                                      timeMax=end_time,
                                                      timeMin=start_time).execute()

        return events


    def get_calendars_summary(self):
        """
        returns [(id, name), ...,] for each calendar in db for given user
        """
        return [(x.id, x.name) for x in CalendarModel.objects.all().filter(user__username=self.user.username)]


    def create_graphs(self, calendars_list, periods_type):
        """
        takes what to show on graphs in 2 lists
        plots it with matplolib
        saves images in /BASE_DIR/<username> 
        """
        # all events stored by calendar_id
        events = {}
        # create folder to store images
        folder  = os.path.join(settings.BASE_DIR, 'graphs/'+self.user.username)
        if not os.path.exists(folder):
            os.makedirs(folder)

        for calendar_id in calendars_list:
            for period_type in periods_type:
                PeriodModel.objects.create_period(calendar_id, period_type)
            

        return (0, 0, 0)

