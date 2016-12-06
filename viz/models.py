from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from datetime import datetime, timedelta, date
import calendar as calendar_module


class CalendarModel(models.Model):
    id = models.CharField(max_length=150, primary_key=True)
    name = models.CharField(max_length=100) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name +'#'+ self.user.username


class CalendarAdmin(admin.ModelAdmin):
    pass


admin.site.register(CalendarModel, CalendarAdmin)


class PeriodManager(models.Manager):
    def create_period(self, calendar_id, period_type):
        calendar = CalendarModel.objects.get(id=calendar_id)
        now   = datetime.now()
        start = datetime.utcnow()
        end   = datetime.utcnow()
        delta = datetime.utcnow()

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

        return self.create(start=start, end=end, delta=delta, calendar=calendar)


class PeriodModel(models.Model):
    start    = models.DateTimeField()
    end      = models.DateTimeField()
    delta    = models.DurationField()
    objects  = PeriodManager()
    calendar = models.ForeignKey(CalendarModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.calendar.name
    