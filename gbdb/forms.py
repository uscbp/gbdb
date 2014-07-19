from django import forms
from registration.forms import RegistrationForm

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