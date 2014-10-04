from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import BaseCreateView
from gbdb.models import SavedLocation
from uscbp.views import JSONResponseMixin

class SavedLocationDetailView(JSONResponseMixin, BaseDetailView):

    def get(self, request, *args, **kwargs):
        # Load similar models
        location=SavedLocation.objects.get(id=self.request.GET['id'])

        data = {'name': location.name,
                'latitude': float(location.latitude),
                'longitude': float(location.longitude)}

        return self.render_to_response(data)


class CreateSavedLocationView(JSONResponseMixin,BaseCreateView):
    model = SavedLocation

    def get_context_data(self, **kwargs):
        context={'msg':u'No POST data sent.' }
        if self.request.is_ajax():
            if 'name' in self.request.POST and len(self.request.POST['name']) and 'latitude' in self.request.POST and \
               len(self.request.POST['latitude']) and 'longitude' in self.request.POST and \
               len(self.request.POST['longitude']):
                if not SavedLocation.objects.filter(name=self.request.POST['name']).count():
                    location=SavedLocation(name=self.request.POST['name'], latitude=float(self.request.POST['latitude']),
                        longitude=float(self.request.POST['longitude']))
                else:
                    location=SavedLocation.objects.get(name=self.request.POST['name'])
                    location.latitude=float(self.request.POST['latitude'])
                    location.longitude=float(self.request.POST['longitude'])
                location.save()
                context = {'id': location.id, 'name': location.name}
        return context