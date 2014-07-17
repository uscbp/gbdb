from django.contrib import admin
from gbdb.models import ObservationSession, BehavioralEvent, Gesture, Primate, Context, Ethogram, BodyPart

class BehavioralEventInline(admin.StackedInline):
    model = BehavioralEvent
    extra = 0
    
class ObservationSessionAdmin(admin.ModelAdmin):
    inlines = [BehavioralEventInline]
    
class GestureInline(admin.StackedInline):
    model = Gesture
    extra = 0
    
class BehavioralEventAdmin(admin.ModelAdmin):
    inlines = [GestureInline]
    

admin.site.register(ObservationSession, ObservationSessionAdmin)
admin.site.register(BehavioralEvent, BehavioralEventAdmin)
admin.site.register(Gesture)
admin.site.register(Primate)
admin.site.register(Context)
admin.site.register(Ethogram)
admin.site.register(BodyPart)
