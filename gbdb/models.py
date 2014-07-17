from django.db import models


class Species(models.Model):
    genus_name = models.CharField(max_length=100)
    species_name = models.CharField(max_length=100)
    common_name = models.CharField(max_length=100)
    
    class Meta:
        app_label='gbdb'


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
        
        
class Context(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label='gbdb'
        
        
class Ethogram(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label='gbdb'
    
    
class ObservationSession(models.Model):
    video = models.FileField(upload_to='videos/observation_session/%Y/%m/%d')
    date = models.DateField()
    location = models.CharField(max_length=100) #this should be some kind of geo model
    notes = models.TextField()
    
    class Meta:
        app_label='gbdb'
        
        
class BehavioralEvent(models.Model):
    observation_session=models.ForeignKey(ObservationSession)
    start_time = models.TimeField()
    duration = models.IntegerField()
    video = models.FileField(upload_to='videos/behavioral_event/%Y/%m/%d')
    primates = models.ManyToManyField(Primate)
    contexts = models.ManyToManyField(Context)
    ethograms = models.ManyToManyField(Ethogram)
    notes = models.TextField()
    
    class Meta:
        app_label='gbdb'
        
        
class BodyPart(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label='gbdb'
        
        
class Gesture(models.Model):
    CHOICES = (
        ('yes', 'Yes'),
        ('no', 'No'),
        )

    behavioral_event=models.ForeignKey(BehavioralEvent)
    start_time = models.TimeField()
    duration = models.IntegerField()
    goal = models.TextField(blank=True)
    signaller = models.ForeignKey('Primate', related_name='signaller')
    recipient = models.ForeignKey('Primate', related_name='recipient')
    signaller_body_parts = models.ManyToManyField(BodyPart, related_name='signaller_body_part')
    recipient_body_parts = models.ManyToManyField(BodyPart, related_name='recipient_body_part')
    audible = models.CharField(max_length=100, choices=CHOICES, default='no')
    recipient_response = models.TextField()
    goal_met = models.CharField(max_length=100, choices=CHOICES, default='no')
    notes = models.TextField()
    
    class Meta:
        app_label='gbdb'
        