from django.contrib import admin
from .models import Calendar

class CalendarAdmin(admin.ModelAdmin):
    pass


admin.site.register(Calendar, CalendarAdmin)
