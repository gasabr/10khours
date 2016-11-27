from django import forms

PERIODS = (
  ('this_month', 'this month'),
  ('this_week', 'this week'),
  ('today', 'today'),
)


class ChoiceForm(forms.Form):
  period   = forms.ChoiceField(choices=PERIODS, required=True)
  keywords = forms.CharField(required=False)
  
  def __init__(self, *args, **kwargs):
    calendars_list = kwargs.pop('calendars_list')+[('all', 'all')]
    super(ChoiceForm, self).__init__(*args, **kwargs)
    self.fields['calendar'] = forms.ChoiceField(choices=calendars_list)

  class Meta:
    fields = ['period', 'calendar', 'keywords']
