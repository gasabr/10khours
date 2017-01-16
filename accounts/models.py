from django.db import models
from django.contrib.auth.models import User

REPEAT_CHOICES = [
    ('every_day','Every Day'),
    ('every_week', 'every Week'),
    ('every_month','every Month')
]
# TODO: sync this PERIODS with source
# from viz/forms.py
PERIOD_CHOICES = [
    ('this_month', 'this month'),
    ('last_30_days', 'last 30 days'),
    ('this_week', 'this week'),
]

class Schedule(models.Model):
    """model to store user email delivery schedule

    Fields descriptions:
    next_run -- the next time scheduled events should be executed
    repeat   -- when to repeat sending (start + repeat = next_run)
    periods  -- what periods should be included in report
    """
    user     = models.OneToOneField(User, primary_key=True)
    start    = models.DateField()
    end      = models.DateField()
    next_run = models.DateTimeField()
    repeat   = models.CharField(max_length=20, choices=REPEAT_CHOICES)
    periods  = models.CharField(max_length=20, choices=PERIOD_CHOICES)
