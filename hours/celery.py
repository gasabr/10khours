from __future__ import absolute_import
import os
# Fix to 'Apps are not loaded'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hours.settings")
import django
django.setup()


from celery import Celery
from datetime import datetime
# from viz.tasks import shared_test
from django.contrib.auth import get_user_model

from accounts.models import Schedule




app = Celery('tasks', backend='redis://localhost', broker='redis://localhost')
app.config_from_object('django.conf:settings')


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0,
                             check_schedules.s('hello'),
                             name='add every 10'
                            )


@app.task
def check_schedules(arg):
    """Checks schedules in db if anything should be sent now."""
    # schedules where next_run earlier or now
    to_send = Schedule.objects.filter(next_run__lte=datetime.now())
    # send emails

    # refresh next_run
    # new_next_run = s.next_run + get_delta(s.repeat)

    print(len(to_send))


def get_delta(repeat):
    """Will calculate and return timedelta for repeat period."""
    delta = timedelta(days=1)
    if repeat == 'every_week'  : delta = timedelta(days=7)
    if repeat == 'every_day'   : delta = timedelta(days=1)
    # TODO: amount of days in current month here
    if repeat == 'every_month' : delta = timedelta(days=30)
    return delta
