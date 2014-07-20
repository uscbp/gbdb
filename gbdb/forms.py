import datetime
from django.forms.extras import SelectDateWidget
from django import forms
from gbdb.models import ObservationSession
from registration.forms import RegistrationForm
from registration.models import User

class GbdbRegistrationForm(RegistrationForm):
    """
    Extends the basic registration form with support for fields required by BODB.
        - first_name, last_name, and affiliation
    """
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    def save(self, profile_callback=None):
        """
        Override RegistrationForm.save() so that we can commit the first_name and last_name to the
        user object and the affiliation to the user profile object.
        """

        # First, save the parent form
        new_user = super(GbdbRegistrationForm, self).save(profile_callback=profile_callback)

        # Update user with first, last names
        new_user.first_name = self.cleaned_data['first_name']
        new_user.last_name = self.cleaned_data['last_name']
        new_user.save()

        return new_user


class ObservationSessionForm(forms.ModelForm):
    collator = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput,required=False)

    video = forms.FileField(required=False)
    date = forms.DateField(widget=SelectDateWidget(years=range(1950, datetime.date.today().year+10)), required=True)
    location = forms.CharField(widget=forms.TextInput(attrs={'size':'100'}),required=True)
    notes = forms.CharField(widget=forms.Textarea(attrs={'cols':'57','rows':'5'}),required=False)

    class Meta:
        model=ObservationSession