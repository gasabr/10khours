from django import forms

PERIODS = (
    ('this_month', 'this month'),
    ('last_30_days', 'last 30 days'),
    ('this_week', 'this week'),
    ('today', 'today'),
)


class ChoiceForm(forms.Form):
    """
    Form on 10khours.ru/viz/
    Fields:
        period   : one of the PERIODS above
        keywords : future feature
        calendar : choice field based on user's calendars
    """
    period   = forms.ChoiceField(choices=PERIODS, required=True)
    keywords = forms.CharField(required=False)
    refresh  = forms.BooleanField()
    

    def __init__(self, *args, **kwargs):
        calendars_list = kwargs.pop('calendars_list')+[('primary', 'primary')]
        super(ChoiceForm, self).__init__(*args, **kwargs)

        self.fields['calendar'] = forms.ChoiceField(choices=calendars_list)

    class Meta:
        fields = ['period', 'calendar', 'keywords']
