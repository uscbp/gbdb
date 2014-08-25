import os
import subprocess
from django.core.urlresolvers import reverse
from django.db import models
from geoposition.fields import GeopositionField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from registration.models import User
from uscbp import settings

from django.utils.encoding import force_unicode
import os.path

class RenameFilesModel(models.Model):
    """
    Abstract model implementing a two-phase save in order to rename
    `FileField` and `ImageField` filenames after saving.  This allows the
    final filenames to contain information like the primary key of the model.

    Example:

        class Photo(RenameFilesModel):
            file = models.ImageField(upload_to='uploads/temp')

            RENAME_FILES = {
                'file': {'dest': 'uploads/photos', 'keep_ext': True}
            }

        >>> photo = Photo(file='uploads/temp/photo.jpg')
        >>> photo.pk

        >>> photo.save()
        >>> photo.pk
        1
        >>> photo.file
        <ImageFieldFile: uploads/photos/1.jpg>

    If the 'dest' option is a callable, it will be called with the model
    instance (guaranteed to be saved) and the currently saved filename, and
    must return the new filename.  Otherwise, the filename is determined by
    'dest' and the model's primary key.

    If a file already exists at the resulting path, it is deleted.  This is
    desirable if the filename should always be the primary key, for instance.
    To avoid this behavior, write a 'dest' handler that results in a unique
    filename.

    If 'keep_ext' is True (the default), the extension of the previously saved
    filename will be appended to the primary key to construct the filename.
    The value of 'keep_ext' is not considered if 'dest' is a callable.

    """
    RENAME_FILES = {}

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False):
        rename_files = getattr(self, 'RENAME_FILES', None)
        if rename_files:
            super(RenameFilesModel, self).save(force_insert, force_update)
            force_insert, force_update = False, True

            for field_name, options in rename_files.iteritems():
                field = getattr(self, field_name)
                file_name = force_unicode(field)
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

        super(RenameFilesModel, self).save(force_insert, force_update)

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
                cmds=['avconv', '-i', orig_filename, '-vcodec', 'libx264', mp4_filename]
                subprocess.call(cmds)
            ogg_filename='%s.ogg' % root
            if not os.path.exists(ogg_filename):
                cmds=['ffmpeg2theora', orig_filename, '-o', ogg_filename]
                subprocess.call(cmds)
            swf_filename='%s.swf' % root
            if not os.path.exists(swf_filename):
                cmds=['ffmpeg', '-i', orig_filename, swf_filename]
                subprocess.call(cmds)
        
        
class BehavioralEvent(MPTTModel):
    observation_session=models.ForeignKey(ObservationSession, null=True, blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    type = models.CharField(max_length=45, blank=False, null=False, default='generic')
    start_time = models.TimeField(blank=True, null=True)
    duration = models.TimeField(blank=True, null=True)
    video = models.FileField(upload_to='videos/behavioral_event/%Y/%m/%d',  blank=True, null=True)
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

    def segment_video(self, parent_video_name):
        parent_root, parent_ext = os.path.splitext(parent_video_name)
        start_time_string = '%d:%d:%d.%d' % (self.start_time.hour, self.start_time.minute, self.start_time.second,
                                             self.start_time.microsecond)
        duration_string = '%d:%d:%d.%d' % (self.duration.hour, self.duration.minute, self.duration.second,
                                           self.duration.microsecond)
        new_path = os.path.join(settings.MEDIA_ROOT, 'videos', 'behavioral_event')
        mp4_filename = os.path.join(new_path, '%d.mp4' % self.id)
        if not os.path.exists(mp4_filename):
            cmds = ['ffmpeg', '-i', '%s.mp4' % os.path.join(settings.MEDIA_ROOT,parent_root), '-ss', start_time_string,
                    '-t', duration_string, '-vcodec', 'libx264', mp4_filename]
            print(cmds)
            subprocess.call(cmds)
        ogg_filename = os.path.join(new_path, '%d.ogg' % self.id)
        if not os.path.exists(ogg_filename):
            cmds = ['ffmpeg2theora', mp4_filename, '-o', ogg_filename]
            subprocess.call(cmds)
        swf_filename = os.path.join(new_path, '%d.swf' % self.id)
        if not os.path.exists(swf_filename):
            cmds = ['ffmpeg', '-i', mp4_filename, '-ss', start_time_string, '-t', duration_string, swf_filename]
            subprocess.call(cmds)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        rename_files = getattr(self, 'RENAME_FILES', None)
        if rename_files and self.video.name:
            super(ObservationSession, self).save(force_insert, force_update)
            force_insert, force_update = False, True

            for field_name, options in rename_files.iteritems():
                field = getattr(self, field_name)
                file_name = force_unicode(field)
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
                cmds=['avconv', '-i', orig_filename, '-vcodec', 'libx264', mp4_filename]
                print(cmds)
                subprocess.call(cmds)
            ogg_filename='%s.ogg' % root
            if not os.path.exists(ogg_filename):
                cmds=['ffmpeg2theora', orig_filename, '-o', ogg_filename]
                subprocess.call(cmds)
            swf_filename='%s.swf' % root
            if not os.path.exists(swf_filename):
                cmds=['ffmpeg', '-i', orig_filename, swf_filename]
                subprocess.call(cmds)
        else:
            if self.parent is None or self.parent.video.name is None:
                self.segment_video(self.observation_session.video.name)
            else:
                self.segment_video(self.parent.video.name)

        
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
