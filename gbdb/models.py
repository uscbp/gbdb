import os
import subprocess
from django.core.urlresolvers import reverse
from django.db import models
from geoposition.fields import GeopositionField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from registration.models import User
from uscbp import settings


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
    location_name = models.CharField(max_length=100) #this should be some kind of geo model
    location = GeopositionField()
    habitat = models.CharField(max_length=100, choices=HABITAT_CHOICES, default='wild')
    class Meta:
        app_label='gbdb'
        
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('primate_view', kwargs={'pk': self.pk})
        
        
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
    location_name = models.CharField(max_length=100) #this should be some kind of geo model
    location = GeopositionField()
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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        convert_video=False
        if not self.id:
            convert_video=True
        super(ObservationSession,self).save(force_insert=force_insert, force_update=force_update, using=using,
            update_fields=update_fields)

        if convert_video and self.video.name:
            print(self.video.name)
            orig_filename=os.path.join(settings.MEDIA_ROOT,self.video.name)
            root,ext=os.path.splitext(orig_filename)
            #cmds=['ffmpeg','-i',orig_filename,'-vcodec', 'libx264', '-acodec', 'aac', '-strict', '-2', '%s.mp4' % root]
            cmds=['avconv', '-i', orig_filename, '-vcodec', 'libx264', '%s.mp4' % root]
            subprocess.call(cmds)
            cmds=['ffmpeg2theora', orig_filename, '-o', '%s.ogg' % root]
            subprocess.call(cmds)
            cmds=['ffmpeg', '-i', orig_filename, '%s.swf' % root]
        
        
class BehavioralEvent(MPTTModel):
    observation_session=models.ForeignKey(ObservationSession, null=True, blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    type = models.CharField(max_length=45, blank=False, null=False, default='generic')
    start_time = models.TimeField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
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
    signaller = models.ForeignKey('Primate', related_name='signaller', null=True)
    recipient = models.ForeignKey('Primate', related_name='recipient', null=True)
    gesture = models.ForeignKey('Gesture', related_name='gesture', null=True)
    recipient_response = models.TextField()
    goal_met = models.CharField(max_length=100, choices=CHOICES, default='no')
    
    class Meta:
        app_label='gbdb'

    def get_absolute_url(self):
        return reverse('gestural_event_view', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        self.type='gestural'
        super(GesturalEvent,self).save(*args, **kwargs)


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

    def get_absolute_url(self):
        return reverse('gesture_view', kwargs={'pk': self.pk})
