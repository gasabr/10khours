from datetime import datetime, time


class Period():
  """
  Class to handle periods of time in app:
    - get dates, delta from type
    - spliting period to subperiods
    - spreading events to subperiods
    - counting summary duration of events in subperiods
  """
  def __init__(self, period_type):
    """
    Parameter:
      period_type : str, one of the PERIODS in views.py
    Initialized fields:
      start : datetime.datetime
      end   : datetime.datetime
      delta : datetime.timedelta
    """
    now   = datetime.now()   
    start = datetime.utcnow()
    end   = datetime.utcnow()
    delta = datetime.utcnow()

    if period == 'this_month':
      self.start = datetime.combine(date(now.year, now.month, 1), datetime.min.time())
      self.end   = datetime.combine(date(now.year, now.month, calendar.monthrange(now.year, now.month)[1]),
                             datetime.min.time())
      delta = timedelta(days=1)
    elif period == 'today':
      self.start = datetime.combine(start, datetime.min.time())
      self.end   = datetime.combine(start, datetime.max.time())
      self.delta = timedelta(hours=1)
    elif period == 'this_week':
      self.start = datetime.combine(date(now.year, now.month, now.day) - timedelta(days=now.weekday()), datetime.min.time())
      self.end   = start + timedelta(days=6)
      self.delta = timedelta(days=1)
    
