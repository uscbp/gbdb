import datetime
from django.forms import TimeInput
from django.forms.models import inlineformset_factory
from django.forms.extras import SelectDateWidget
from django import forms
from gbdb.models import ObservationSession, BehavioralEvent, Primate, Context, Ethogram, Species, Gesture, BodyPart, GesturalEvent
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
    location = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}),required=True)
    notes = forms.CharField(widget=forms.Textarea(attrs={'cols':'57','rows':'5'}),required=False)

    class Meta:
        model=ObservationSession


class BehavioralEventForm(forms.ModelForm):
    observation_session=forms.ModelChoiceField(queryset=ObservationSession.objects.all(),widget=forms.HiddenInput,
        required=False)
    parent=forms.ModelChoiceField(queryset=BehavioralEvent.objects.all(),widget=forms.HiddenInput, required=False)
    start_time = forms.TimeField(widget=TimeInput(), required=True)
    duration = forms.CharField(widget=forms.TextInput(attrs={'size':'20'}),required=True)
    video = forms.FileField(required=False)
    primates = forms.ModelMultipleChoiceField(queryset=Primate.objects.all(), widget=forms.MultipleHiddenInput,
        required=False)
    contexts = forms.ModelMultipleChoiceField(queryset=Context.objects.all(), widget=forms.MultipleHiddenInput,
        required=False)
    ethograms = forms.ModelMultipleChoiceField(queryset=Ethogram.objects.all(), widget=forms.MultipleHiddenInput,
        required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={'cols':'57','rows':'5'}),required=False)

    class Meta:
        model=BehavioralEvent


BaseBehavioralEventFormSet = inlineformset_factory(ObservationSession, BehavioralEvent, form=BehavioralEventForm,
    fk_name='observation_session', extra=0, can_delete=True, can_order=True)


SubBehavioralEventFormSet = inlineformset_factory(BehavioralEvent, BehavioralEvent, form=BehavioralEventForm,
    fk_name='parent', extra=0, can_delete=True, can_order=True)


class GesturalEventForm(BehavioralEventForm):
    signaller = forms.ModelChoiceField(queryset=Primate.objects.all(), required=False)
    recipient = forms.ModelChoiceField(queryset=Primate.objects.all(), required=False)
    gesture = forms.ModelChoiceField(queryset=Gesture.objects.all(), required=False)
    recipient_response = forms.CharField(widget=forms.Textarea(attrs={'cols':'57','rows':'5'}),required=False)
    goal_met = forms.ChoiceField(choices=GesturalEvent.CHOICES,
        widget=forms.Select(attrs={'style': 'font-size: 80%;font-family: verdana, sans-serif'}), required=True)

    class Meta:
        model=GesturalEvent


GesturalEventFormSet = inlineformset_factory(BehavioralEvent, GesturalEvent, form=GesturalEventForm, fk_name='parent',
    extra=0, can_delete=True, can_order=True)


class PrimateForm(forms.ModelForm):
    
    name = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}),required=True)
    species = forms.ModelChoiceField(queryset=Species.objects.all(), required=True)
    birth_date = forms.DateField(widget=SelectDateWidget(years=range(1950, datetime.date.today().year+10)), required=True)
    location = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}),required=True)
    habitat = forms.ChoiceField(choices=Primate.HABITAT_CHOICES, widget=forms.Select(), required=True)
    

    class Meta:
        model=Primate
        
        
class GestureForm(forms.ModelForm):
    
    name = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}),required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'cols':'57','rows':'5'}),required=False)
    goal = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}),required=True)
    signaller_body_parts = forms.ModelMultipleChoiceField(queryset=BodyPart.objects.all(), required=False)
    recipient_body_parts = forms.ModelMultipleChoiceField(queryset=BodyPart.objects.all(), required=False)
    audible = forms.ChoiceField(choices=Gesture.CHOICES, widget=forms.Select(), required=True)
    

    class Meta:
        model=Gesture
        
        