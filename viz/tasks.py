from celery import shared_task
from celery.schedules import crontab


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # Calls test('hello') every 10 seconds.
#     sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

#     # Calls test('world') every 30 seconds
#     sender.add_periodic_task(5.0, summ.delay(1, 1))


@shared_task
def shared_test(arg):
    print(arg)

@shared_task
def summ(i : int, j : int) -> int:
	print(i + j)