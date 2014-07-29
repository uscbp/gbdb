from django.core.urlresolvers import reverse
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from registration.models import User


class Species(models.Model):
    genus_name = models.CharField(max_length=100)
    species_name = models.CharField(max_length=100)
    common_name = models.CharField(max_length=100)
    
    class Meta:
        app_label='gbdb'
        
    def __unicode__(self):
        return self.common_name


class Primate(models.Model):
    HABITAT_CHOICES = (
        ('captive', 'Captive'),
        ('wild', 'Wild'),
        )
    name = models.CharField(max_length=100)
    species = models.ForeignKey(Species)
    birth_date = models.DateField()
    location = models.CharField(max_length=100) #this should be some kind of geo model
    habitat = models.CharField(max_length=100, choices=HABITAT_CHOICES, default='wild')
    class Meta:
        app_label='gbdb'
        
    def __unicode__(self):
        return self.name
        
        
class Context(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label='gbdb'
        
    def __unicode__(self):
        return self.name
        
        
class Ethogram(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label='gbdb'
        
    def __unicode__(self):
        return self.name
    
    
class ObservationSession(models.Model):
    collator = models.ForeignKey(User,null=True)
    creation_time = models.DateTimeField(auto_now_add=True,blank=True)
    last_modified_time = models.DateTimeField(auto_now=True,blank=True)
    last_modified_by = models.ForeignKey(User,null=True,blank=True,related_name='last_modified_by')

    video = models.FileField(upload_to='videos/observation_session/%Y/%m/%d',  blank=True, null=True)
    date = models.DateField()
    location = models.CharField(max_length=100) #this should be some kind of geo model
    notes = models.TextField()
    
    class Meta:
        app_label='gbdb'

    def get_absolute_url(self):
        return reverse('observation_session_view', kwargs={'pk': self.pk})

    def get_collator_str(self):
        if self.collator.last_name:
            return '%s %s' % (self.collator.first_name, self.collator.last_name)
        else:
            return self.collator.username

    def get_modified_by_str(self):
        if self.last_modified_by.last_name:
            return '%s %s' % (self.last_modified_by.first_name, self.last_modified_by.last_name)
        else:
            return self.last_modified_by.username

    def get_created_str(self):
        return self.creation_time.strftime('%B %d, %Y')

    def get_modified_str(self):
        return self.last_modified_time.strftime('%B %d, %Y')
        
        
class BehavioralEvent(MPTTModel):
    observation_session=models.ForeignKey(ObservationSession)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    start_time = models.TimeField()
    duration = models.IntegerField()
    video = models.FileField(upload_to='videos/behavioral_event/%Y/%m/%d',  blank=True, null=True)
    primates = models.ManyToManyField(Primate)
    contexts = models.ManyToManyField(Context)
    ethograms = models.ManyToManyField(Ethogram)
    notes = models.TextField()
    
    class Meta:
        app_label='gbdb'

    def get_absolute_url(self):
        return reverse('behavioral_event_view', kwargs={'pk': self.pk})

        
class BodyPart(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label='gbdb'
        
    def __unicode__(self):
        return self.name
        
        
class GesturalEvent(BehavioralEvent):
    CHOICES = (
        ('yes', 'Yes'),
        ('no', 'No'),
        )
    signaller = models.ForeignKey('Primate', related_name='signaller')
    recipient = models.ForeignKey('Primate', related_name='recipient')
    gesture = models.ForeignKey('Gesture', related_name='gesture')
    recipient_response = models.TextField()
    goal_met = models.CharField(max_length=100, choices=CHOICES, default='no')
    
    class Meta:
        app_label='gbdb'


class Gesture(models.Model):
    CHOICES = (
        ('yes', 'Yes'),
        ('no', 'No'),
        )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    goal = models.TextField(blank=True)
    signaller_body_parts = models.ManyToManyField(BodyPart, related_name='signaller_body_part')
    recipient_body_parts = models.ManyToManyField(BodyPart, related_name='recipient_body_part')
    audible = models.CharField(max_length=100, choices=CHOICES, default='no')

    class Meta:
        app_label='gbdb'
        
    def __unicode__(self):
        return self.name