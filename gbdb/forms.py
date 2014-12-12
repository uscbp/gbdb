import datetime
from django.forms import TimeInput, HiddenInput
from django.forms.models import inlineformset_factory
from django.forms.extras import SelectDateWidget
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from gbdb.models import ObservationSession, BehavioralEvent, Primate, Context, Ethogram, Species, Gesture, BodyPart, GesturalEvent, SavedLocation, Goal
from geoposition.forms import GeopositionField
from registration.forms import RegistrationForm
from registration.models import User

import autocomplete_light

SEARCH_CHOICES = (
    ('all', 'all'),
    ('any', 'any')
    )

HABITAT_CHOICES = (
    ('', ''),
    ('captive', 'Captive'),
    ('wild', 'Wild'),
    )

GENDER_CHOICES = (
    ('',''),
    ('male','male'),
    ('female','female'),
    ('unknown','unknown'),
)

YESNO_CHOICES = (
    ('', ''),
    ('yes', 'Yes'),
    ('no', 'No'),
    )

class GbdbRegistrationForm(RegistrationForm):
    """
    Extends the basic registration form with support for fields required by GBDB.
        - first_name, last_name
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
    saved_locations = forms.ModelChoiceField(queryset=SavedLocation.objects.all(),
        widget=forms.Select(attrs={"onChange":'populateLocation()'}),required=False)
    location_name = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}),required=True)
    location = GeopositionField(required=True)
    notes = forms.CharField(widget=forms.Textarea(attrs={'cols':'57','rows':'5'}),required=False)

    class Meta:
        model=ObservationSession


class ObservationSessionSearchForm(forms.Form):
    created_from = forms.DateTimeField(help_text="Earliest creation date", widget=forms.DateTimeInput, required=False)
    created_to = forms.DateTimeField(help_text="Latest creation date", widget=forms.DateTimeInput, required=False)
    collator = forms.BooleanField(help_text="Only search your entries", required=False)
    username = forms.CharField(help_text='Username of the collator',required=False)
    first_name = forms.CharField(help_text='First name of the collator',required=False)
    last_name = forms.CharField(help_text='Last name of the collator',required=False)
    keywords = forms.CharField(help_text="Keyword search", required=False)
    keywords_options=forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)
    date_min=forms.DateField(widget=SelectDateWidget(years=range(1950, datetime.date.today().year+10)), required=False)
    date_max=forms.DateField(widget=SelectDateWidget(years=range(1950, datetime.date.today().year+10)), required=False)
    location_name=forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
    location_name_options=forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)
    location = GeopositionField(use_radius=True, required=False)
    radius = forms.CharField(help_text='Radius to search in', required=False)
    search_options = forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)


class BehavioralEventForm(forms.ModelForm):
    TYPE_CHOICES = (
        ('generic', 'Generic'),
        ('gestural', 'Gestural')
    )
    type=forms.ChoiceField(choices=TYPE_CHOICES,
        widget=forms.Select(attrs={'onchange': 'updateBehavioralEventOptions(this.value)'}), help_text='Type of event',
        required=True)
    observation_session=forms.ModelChoiceField(queryset=ObservationSession.objects.all(),widget=forms.HiddenInput,
        required=False)
    parent=forms.ModelChoiceField(queryset=BehavioralEvent.objects.all(),widget=forms.HiddenInput, required=False)
    start_time = forms.CharField(widget=HiddenInput(), required=False)
    duration = forms.CharField(widget=HiddenInput(), required=False)
    video = forms.FileField(required=False)
    primates = forms.ModelMultipleChoiceField(queryset=Primate.objects.all(), widget=forms.SelectMultiple(),
        required=False)
    contexts = forms.ModelMultipleChoiceField(queryset=Context.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('ContextAutocomplete'), required=False)
    ethograms = forms.ModelMultipleChoiceField(queryset=Ethogram.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('EthogramAutocomplete'), required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={'cols':'57','rows':'5'}),required=False)
    signaller = forms.ModelChoiceField(queryset=Primate.objects.all(), required=False)
    recipient = forms.ModelChoiceField(queryset=Primate.objects.all(), required=False)
    gesture = forms.ModelChoiceField(queryset=Gesture.objects.all(), required=False)
    recipient_response = forms.CharField(widget=forms.Textarea(attrs={'cols':'57','rows':'5'}),required=False)
    goal_met = forms.ChoiceField(choices=GesturalEvent.CHOICES,
        widget=forms.Select(attrs={'style': 'font-size: 80%;font-family: verdana, sans-serif'}), required=False)

    class Meta:
        model=BehavioralEvent


BaseBehavioralEventFormSet = inlineformset_factory(ObservationSession, BehavioralEvent, form=BehavioralEventForm,
    fk_name='observation_session', extra=0, can_delete=True, can_order=True)


class SubBehavioralEventForm(BehavioralEventForm):
    primates = forms.ModelMultipleChoiceField(queryset=Primate.objects.all(), widget=forms.SelectMultiple(), required=False)

    class Meta:
        model=BehavioralEvent


SubBehavioralEventFormSet = inlineformset_factory(BehavioralEvent, BehavioralEvent, form=SubBehavioralEventForm,
    fk_name='parent', extra=0, can_delete=True, can_order=True)


class BehavioralEventSearchForm(forms.Form):
    TYPE_CHOICES = (
        ('', ''),
        ('generic', 'Generic'),
        ('gestural', 'Gestural')
    )
    type = forms.ChoiceField(choices=TYPE_CHOICES, help_text='Type of Behavioral Event', required=False,
        widget=forms.Select(attrs={'onchange': 'updateBehavioralEventSearchOptions(this.value)'}))
    created_from = forms.DateTimeField(help_text="Earliest creation date", widget=forms.DateTimeInput, required=False)
    created_to = forms.DateTimeField(help_text="Latest creation date", widget=forms.DateTimeInput, required=False)
    collator = forms.BooleanField(help_text="Only search your entries", required=False)
    username = forms.CharField(help_text='Username of the collator',required=False)
    first_name = forms.CharField(help_text='First name of the collator',required=False)
    last_name = forms.CharField(help_text='Last name of the collator',required=False)
    keywords = forms.CharField(help_text="Keyword search", required=False)
    keywords_options=forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)
    date_min=forms.DateField(widget=SelectDateWidget(years=range(1950, datetime.date.today().year+10)), required=False)
    date_max=forms.DateField(widget=SelectDateWidget(years=range(1950, datetime.date.today().year+10)), required=False)
    location_name=forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
    location_name_options=forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)
    location = GeopositionField(use_radius=True, required=False)
    radius = forms.CharField(help_text='Radius to search in', required=False)
    primates_name=forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
    primates_species=forms.ModelMultipleChoiceField(queryset=Species.objects.all(), required=False)
    primates_birth_date_min=forms.DateField(widget=SelectDateWidget(years=range(1950, datetime.date.today().year+10)),
        required=False)
    primates_birth_date_max=forms.DateField(widget=SelectDateWidget(years=range(1950, datetime.date.today().year+10)),
        required=False)
    primates_habitat=forms.ChoiceField(choices=HABITAT_CHOICES, help_text='Primate habitat', required=False)
    contexts = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
    contexts_options=forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)
    ethograms = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
    ethograms_options=forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)
    gestural_signaller_name=forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
    gestural_signaller_species=forms.ModelMultipleChoiceField(queryset=Species.objects.all(), required=False)
    gestural_signaller_birth_date_min=forms.DateField(widget=SelectDateWidget(years=range(1950, datetime.date.today().year+10)),
        required=False)
    gestural_signaller_birth_date_max=forms.DateField(widget=SelectDateWidget(years=range(1950, datetime.date.today().year+10)),
        required=False)
    gestural_signaller_habitat=forms.ChoiceField(choices=HABITAT_CHOICES, help_text='Primate habitat', required=False)
    gestural_recipient_name=forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
    gestural_recipient_species=forms.ModelMultipleChoiceField(queryset=Primate.objects.all(), required=False)
    gestural_recipient_birth_date_min=forms.DateField(widget=SelectDateWidget(years=range(1950, datetime.date.today().year+10)),
        required=False)
    gestural_recipient_birth_date_max=forms.DateField(widget=SelectDateWidget(years=range(1950, datetime.date.today().year+10)),
        required=False)
    gestural_recipient_habitat=forms.ChoiceField(choices=HABITAT_CHOICES, help_text='Primate habitat', required=False)
    gestural_gesture=forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
    gestural_gesture_options=forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)
    gestural_gesture_goal=forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
    gestural_gesture_goal_options=forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)
    gestural_gesture_signaller_body_parts=forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
    gestural_gesture_signaller_body_parts_options=forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options',
        required=False)
    gestural_gesture_recipient_body_parts=forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
    gestural_gesture_recipient_body_parts_options=forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options',
        required=False)
    gestural_gesture_audible=forms.ChoiceField(choices=YESNO_CHOICES, help_text='Audible gesture', required=False)
    gestural_recipient_response=forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
    gestural_recipient_response_options=forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options',
        required=False)
    gestural_goal_met=forms.ChoiceField(choices=YESNO_CHOICES, help_text='Goal of gesture met', required=False)
    search_options = forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)


class PrimateForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}),required=True)
    species = forms.ModelChoiceField(queryset=Species.objects.all(), required=True)
    gender = forms.ChoiceField(choices=Primate.GENDER_CHOICES, widget=forms.Select(), required=True)
    birth_date = forms.DateField(widget=SelectDateWidget(years=range(1950, datetime.date.today().year+10)),
        required=True)
    saved_locations = forms.ModelChoiceField(queryset=SavedLocation.objects.all(),
        widget=forms.Select(attrs={"onChange":'populateLocation()'}),required=False)
    location_name = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}),required=True)
    location = GeopositionField(required=True)
    habitat = forms.ChoiceField(choices=Primate.HABITAT_CHOICES, widget=forms.Select(), required=True)
    

    class Meta:
        model=Primate
        

class PrimateSearchForm(forms.Form):
    name = forms.CharField(help_text="Name search", required=False)
    species=forms.ModelMultipleChoiceField(help_text='Species', queryset=Species.objects.all(), required=False)
    gender=forms.ChoiceField(choices=GENDER_CHOICES, help_text='Gender', required=False)
    birth_date_min=forms.DateField(widget=SelectDateWidget(years=range(1950, datetime.date.today().year+10)),
        required=False)
    birth_date_max=forms.DateField(widget=SelectDateWidget(years=range(1950, datetime.date.today().year+10)),
        required=False)
    location_name=forms.CharField(widget=forms.TextInput(attrs={'size':'30'}), required=False)
    location_name_options=forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)
    location = GeopositionField(use_radius=True, required=False)
    radius = forms.CharField(help_text='Radius to search in', required=False)
    habitat=forms.ChoiceField(choices=HABITAT_CHOICES, help_text='Primate habitat', required=False)
    search_options = forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)


class GestureForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}),required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'cols':'57','rows':'5'}),required=False)
    goal = forms.ModelChoiceField(queryset=Goal.objects.all(), required=True)
    signaller_body_parts = forms.ModelMultipleChoiceField(queryset=BodyPart.objects.all(), required=False)
    recipient_body_parts = forms.ModelMultipleChoiceField(queryset=BodyPart.objects.all(), required=False)
    audible = forms.ChoiceField(choices=Gesture.CHOICES, widget=forms.Select(), required=True)
    

    class Meta:
        model=Gesture


class GestureSearchForm(forms.Form):
    keywords = forms.CharField(help_text="Keyword search", required=False)
    keywords_options=forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)
    name = forms.CharField(help_text="Name search", required=False)
    name_options=forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)
    description = forms.CharField(help_text="Description search", required=False)
    description_options=forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)
    goal = forms.CharField(help_text="Goal search", required=False)
    goal_options=forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)
    signaller_body_parts=forms.ModelMultipleChoiceField(help_text='Signaller body parts',
        queryset=BodyPart.objects.all(), required=False)
    recipient_body_parts=forms.ModelMultipleChoiceField(help_text='Recipient body parts',
        queryset=BodyPart.objects.all(), required=False)
    audible = forms.ChoiceField(choices=YESNO_CHOICES, widget=forms.Select(), required=False)
    search_options = forms.ChoiceField(choices=SEARCH_CHOICES, help_text='Search options', required=False)
