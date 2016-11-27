from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


class CalendarModel(models.Model):
    id = models.CharField(max_length=150, primary_key=True)
    name = models.CharField(max_length=100) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class CalendarAdmin(admin.ModelAdmin):
    pass


admin.site.register(CalendarModel, CalendarAdmin)
