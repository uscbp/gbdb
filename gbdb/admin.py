from django.contrib import admin
from gbdb.models import ObservationSession, BehavioralEvent, GesturalEvent, Gesture, Primate, Context, Ethogram, BodyPart, Species

class BehavioralEventInline(admin.StackedInline):
    model = BehavioralEvent
    extra = 0
    
class GesturalEventInline(admin.StackedInline):
    model = GesturalEvent
    extra = 0
    
class ObservationSessionAdmin(admin.ModelAdmin):
    inlines = [BehavioralEventInline, GesturalEventInline]
    

admin.site.register(ObservationSession, ObservationSessionAdmin)
admin.site.register(BehavioralEvent)
admin.site.register(GesturalEvent)
admin.site.register(Gesture)
admin.site.register(Primate)
admin.site.register(Context)
admin.site.register(Ethogram)
admin.site.register(BodyPart)
admin.site.register(Species)
