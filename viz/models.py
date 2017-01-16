import httplib2
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
import calendar as calendar_module
from django.conf import settings
from apiclient import discovery
from gauth.models import CredentialsModel


def get_duration(event):
    """
    event is { 'start': {'dataTime' : datetime.datetime(),},
               'end'  : {'dataTime' : datetime.datetime(),},
               ...
    returns difference in hours
    """
    try:
        start = event['r_start']['dateTime']
        end   = event['r_end']['dateTime']
    except KeyError:
        # TODO: +03:00 will crash the program for not UTC+3 users
        start = datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S+03:00')
        end   = datetime.strptime(event['end']['dateTime'], '%Y-%m-%dT%H:%M:%S+03:00')
    return float((end-start).seconds / 60) / 60


def clear_event(event):
    """
    will return () for all day and cancelled events
    :returns:
        (start, end) : (datetime.datetime, datetime.datetime) for given event
    """
    # remove cancelled events
    if event['status'] == 'cancelled':
        return ()

    # remove all day events
    if 'date' in event['start'].keys():
        return ()

    # parsing start and end to datetime
    start_dt = datetime.strptime(event['start']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S')
    end_dt   = datetime.strptime(event['end']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S')

    return (start_dt, end_dt)

    # for recurrent events (old API version)
    if 'recurrence' in event.keys():
        return ()

    # for recurrent events (new API version)
    elif 'originalStartTime' in event.keys():
        Start = datetime.strptime(event['originalStartTime']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S')
        End   = Start + (end_dt - start_dt)
        return (Start, End)
    else:
        return (start_dt, end_dt)


class CalendarManager(models.Manager):

    def update_calendars(self, username):
        self.user = User.objects.get(username=username)
        self.creds = CredentialsModel.objects.get(id__username=username).credentials

        # build service to get access to API
        http = self.creds.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=http)

        # calendars in list of dictionaries
        request = self.service.calendarList().list().execute()
        calendars_from_api = request.get('items', [])

        # if there are new calendars add them to db
        for c in calendars_from_api:
            try:
                Calendar.objects.get(id=c['id'])
            except Calendar.DoesNotExist:
                new_calendar = Calendar.objects.create(id=c['id'],
                                                       user=self.user,
                                                       summary=c['summary'])
                new_calendar.save()


    def sync_events(self, calendar_id):
        """
        takes array of calendars ids and time interval
        returns {'calendar_id': [events,...,]}
        """
        bad_recurrence = []

        calendar = Calendar.objects.get(id=calendar_id)
        timeMax  = (datetime.now() + timedelta(days=31)).isoformat() + 'Z'
        timeMin  = (datetime.now() - timedelta(days=31)).isoformat() + 'Z'
        items    = self.service.events().list(calendarId=calendar_id,
                                             timeMin=timeMin,
                                            ).execute().get('items', [])

        performed_icaluids = set()

        for i in items:
            # check event update time in db
            try:
                upd_time = Event.objects.get(id=i['id']).updated
                if upd_time != i['updated']:
                    # delete old event, create new one
                    Event.objects.get(id=i['id']).delete()
                    raise Event.DoesNotExist()
            except Event.DoesNotExist as e:
                # add all recurrence events to items
                if 'recurrence' in i.keys() and i['iCalUID'] not in performed_icaluids:
                    rec_items = self.service.events().instances(calendarId=calendar_id,
                                             eventId=i['id'],
                                             timeMax=timeMax,
                                            ).execute().get('items', [])
                    performed_icaluids.add(i['iCalUID'])
                    for r in rec_items:
                        items.append(r)

                # create new event
                cleaned_date = clear_event(i)
                if len(cleaned_date) == 0:
                    continue
                duration = round(((cleaned_date[1]-cleaned_date[0]).seconds / 3600), 2)
                if duration == 0:
                    return A
                new_event = Event.objects.create(calendar=calendar,
                                                 id=i['id'],
                                                 icaluid=i['iCalUID'],
                                                 summary=i['summary'],
                                                 start=cleaned_date[0],
                                                 end=cleaned_date[1],
                                                 duration=duration,
                                                 updated=datetime.strptime(i['updated'][:-5], '%Y-%m-%dT%H:%M:%S'))

                new_event.save()


    def get_calendars_summary(self):
        """
        returns [(id, name), ...,] for each calendar in db for given user
        """
        return [(x.id, x.summary) for x in Calendar.objects.filter(user__username=self.user.username)]


class Calendar(models.Model):
    """Model to store Google Calendar info"""
    id      = models.CharField(max_length=150, primary_key=True)
    summary = models.CharField(max_length=100)
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    objects = CalendarManager()

    def __str__(self):
        return self.summary +'#'+ self.user.username


class Event(models.Model):
    """Model to store single event info"""
    id       = models.CharField(max_length=100, primary_key=True)
    icaluid  = models.CharField(max_length=100)
    summary  = models.CharField(max_length=150)
    start    = models.DateTimeField()
    end      = models.DateTimeField()
    duration = models.FloatField()
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    updated  = models.DateTimeField()

    def __str__(self):
        return self.summary
