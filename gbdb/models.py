from django.contrib.sites.models import get_current_site
import os
import subprocess
import datetime
from django.core.urlresolvers import reverse
from django.db import models
from geoposition.fields import GeopositionField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from registration.models import User
from uscbp import settings

from django.utils.encoding import force_unicode
import os.path

def convert_to_mp4(mp4_filename, orig_filename, start_time=None, duration=None):
    cmds = ['ffmpeg', '-i', orig_filename]
    if start_time is not None:
        cmds.extend(['-ss', start_time])
    if duration is not None:
        cmds.extend(['-t', duration])
    ext=os.path.splitext(orig_filename)[1]
    cmds.extend(['-vcodec', 'libx264','-acodec', 'libfaac'])
    #this is does not get called on behavioral event chop
    if ext.lower() == '.mov':
        cmds.extend(['-strict', '-2'])
    cmds.append(mp4_filename)
    print('converting to mp4')
    print(cmds)
    subprocess.call(cmds)

#def convert_to_ogg(ogg_filename, orig_filename, start_time=None, end_time=None):
#    cmds=['avconv', '-i', orig_filename]
#    if start_time is not None:
#        cmds.extend(['-ss',start_time])
#    if end_time is not None:
#        cmds.extend(['-t',end_time])
#    cmds.append(ogg_filename)
#    print('converting to ogg')
#    print(cmds)
#    subprocess.call(cmds)

#def convert_to_swf(swf_filename, orig_filename, start_time=None, duration=None):
#    cmds=['avconv', '-i', orig_filename]
#    if start_time is not None:
#        cmds.extend(['-ss', start_time])
#    if duration is not None:
#        cmds.extend(['-t', duration])
#    cmds.extend(['-ar', '44100', swf_filename])
#    print('converting to swf')
#    print(cmds)
#    subprocess.call(cmds)

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
    GENDER_CHOICES = (
        ('male', 'male'),
        ('female', 'female'),
        ('unknown', 'unknown')
    )
    name = models.CharField(max_length=100)
    species = models.ForeignKey(Species)
    birth_date = models.DateField()
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES, default='unknown')
    location_name = models.CharField(max_length=100) #this should be some kind of geo model
    location = GeopositionField()
    habitat = models.CharField(max_length=100, choices=HABITAT_CHOICES, default='wild')
    class Meta:
        app_label='gbdb'
        
    def __unicode__(self):
        return '%s (%s)' % (self.name,self.species)
        
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
    
    video = models.FileField(upload_to='videos/observation_session/temp',  blank=True, null=True)
    date = models.DateField()
    location_name = models.CharField(max_length=100) #this should be some kind of geo model
    location = GeopositionField()
    notes = models.TextField()

    RENAME_FILES = {
        'video': {'dest': 'videos/observation_session', 'keep_ext': True}
    }

    class Meta:
        app_label='gbdb'

    def video_url_mp4(self):
        return ''.join(['http://', get_current_site(None).domain, os.path.join('/media/videos/observation_session','%d.mp4' % self.id)])

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

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        rename_files = getattr(self, 'RENAME_FILES', None)
        if rename_files:
            super(ObservationSession, self).save(force_insert, force_update)
            force_insert, force_update = False, True

            for field_name, options in rename_files.iteritems():
                field = getattr(self, field_name)
                file_name = force_unicode(field)
                if len(file_name):
                    name, ext = os.path.splitext(file_name)
                    keep_ext = options.get('keep_ext', True)
                    final_dest = options['dest']
                    if callable(final_dest):
                        final_name = final_dest(self, file_name)
                    else:
                        final_name = os.path.join(final_dest, '%s' % (self.pk,))
                        if keep_ext:
                            final_name += ext
                    if file_name != final_name:
                        field.storage.delete(final_name)
                        field.storage.save(final_name, field)
                        field.storage.delete(file_name)
                        setattr(self, field_name, final_name)

        super(ObservationSession,self).save(force_insert=force_insert, force_update=force_update, using=using,
            update_fields=update_fields)

        if self.video.name:
            orig_filename=os.path.join(settings.MEDIA_ROOT,self.video.name)
            root,ext=os.path.splitext(orig_filename)
            mp4_filename='%s.mp4' % root
            if not os.path.exists(mp4_filename):
                convert_to_mp4(mp4_filename, orig_filename)
                
    def to_dict(self):
        d = {}
        d['startDate'] = self.date.strftime('%Y,%m,%d')
        d['type'] = "default"
        d['headline'] = "Observation Session"
        d['text'] = "timeline"
        d['asset'] = {'media': "", 'credit': "", 'caption': "" }
        events = []
        for e in self.behavioralevent_set.all():
            events.append(dict([(attr, getattr(e, attr)) for attr in [f.name for f in e._meta.fields]]))
        d['date'] = [ e.to_dict() for e in self.behavioralevent_set.all()]
        timeline = {'timeline': d}
        return timeline

        
class BehavioralEvent(MPTTModel):
    RELATIVE_TO_CHOICES = (
        ('behavioral_event', 'behavioral event'),
        ('observation_session', 'observation session'),
    )
    observation_session=models.ForeignKey(ObservationSession, null=True, blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    type = models.CharField(max_length=45, blank=False, null=False, default='generic')
    start_time = models.TimeField(blank=True, null=True)
    duration = models.TimeField(blank=True, null=True)
    relative_to = models.CharField(max_length=100, choices=RELATIVE_TO_CHOICES, default='observation_session')
    video = models.FileField(upload_to='videos/behavioral_event/temp',  blank=True, null=True)
    primates = models.ManyToManyField(Primate)
    contexts = models.ManyToManyField(Context)
    ethograms = models.ManyToManyField(Ethogram)
    notes = models.TextField()

    RENAME_FILES = {
        'video': {'dest': 'videos/behavioral_event', 'keep_ext': True}
    }

    class Meta:
        app_label='gbdb'

    def get_absolute_url(self):
        return reverse('behavioral_event_view', kwargs={'pk': self.pk})

    def video_url_mp4(self):
        if self.video.name:
            return ''.join(['http://', get_current_site(None).domain, os.path.join('/media/videos/behavioral_event','%d.mp4' % self.id)])
        elif self.parent:
            return self.parent.video_url_mp4()
        else:
            return self.observation_session.video_url_mp4()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        rename_files = getattr(self, 'RENAME_FILES', None)
        if rename_files and self.video.name:
            super(BehavioralEvent, self).save(force_insert, force_update)
            force_insert, force_update = False, True

            for field_name, options in rename_files.iteritems():
                field = getattr(self, field_name)
                file_name = force_unicode(field)
                if len(file_name):
                    name, ext = os.path.splitext(file_name)
                    keep_ext = options.get('keep_ext', True)
                    final_dest = options['dest']
                    if callable(final_dest):
                        final_name = final_dest(self, file_name)
                    else:
                        final_name = os.path.join(final_dest, '%s' % (self.pk,))
                        if keep_ext:
                            final_name += ext
                    if file_name != final_name:
                        field.storage.delete(final_name)
                        field.storage.save(final_name, field)
                        field.storage.delete(file_name)
                        setattr(self, field_name, final_name)

        super(BehavioralEvent,self).save(force_insert=force_insert, force_update=force_update, using=using,
            update_fields=update_fields)

        if self.video.name:
            orig_filename=os.path.join(settings.MEDIA_ROOT,self.video.name)
            root,ext=os.path.splitext(orig_filename)
            mp4_filename='%s.mp4' % root
            if not os.path.exists(mp4_filename):
                convert_to_mp4(mp4_filename, orig_filename)

    def start_time_seconds(self):
        if self.start_time:
            if self.parent is not None:
                if self.parent.video.name is None or not len(self.parent.video.name) and  self.relative_to=='behavioral_event':
                    return self.parent.start_time_seconds()+self.start_time.hour*60*60+self.start_time.minute*60+self.start_time.second
            return self.start_time.hour*60*60+self.start_time.minute*60+self.start_time.second
        return 0

    def end_time_seconds(self):
        return self.start_time_seconds()+self.duration.hour*60*60+self.duration.minute*60+self.duration.second
    
    def to_dict(self):
        d = {}
        #start_datetime = datetime.datetime(0,0,0, self.start_time.hour, self.start_time.minute, self.start_time.second)
        start_datetime = datetime.datetime.combine(self.observation_session.date, self.start_time)
        end_datetime = start_datetime + datetime.timedelta(hours=self.duration.hour, minutes=self.duration.minute, seconds=self.duration.second)
        d['startDate'] = start_datetime.strftime('%Y,%m,%d,%H,%M,%S')
        d['endDate'] = end_datetime.strftime('%Y,%m,%d,%H,%M,%S')
        d['headline'] = "Behavioral Event"
        d['text'] = ""
        d['asset'] = {'media': "", 'credit': "", 'caption': "" }
        return d
        
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


class SavedLocation(models.Model):
    name = models.CharField(max_length=100) #this should be some kind of geo model
    latitude = models.DecimalField(max_digits=10, decimal_places=5)
    longitude = models.DecimalField(max_digits=10, decimal_places=5)

    class Meta:
        app_label='gbdb'

    def __unicode__(self):
        return self.name