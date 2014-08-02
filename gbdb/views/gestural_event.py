from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView
from gbdb.forms import GesturalEventForm
from gbdb.models import GesturalEvent, ObservationSession

class EditGesturalEventMixin():
    model=GesturalEvent
    form_class=GesturalEventForm
    template_name='gbdb/gestural_event/gestural_event_detail.html'

    def form_valid(self, form):
        context = self.get_context_data()
        
        self.object = form.save(commit=False)
        self.object.save()
        form.save_m2m()

        url=self.get_success_url()
        if '_popup' in self.request.GET:
            url+='?_popup=1'
        return redirect(url)


class CreateGesturalEventView(EditGesturalEventMixin, CreateView):

    def get_initial(self):
        initial = super(CreateGesturalEventView,self).get_initial()
        initial['observation_session']=ObservationSession.objects.get(id=self.request.GET.get('observation_session'))
        return initial

    def get_context_data(self, **kwargs):
        context = super(CreateGesturalEventView,self).get_context_data(**kwargs)
        return context


class UpdateGesturalEventView(EditGesturalEventMixin,UpdateView):

    def get_context_data(self, **kwargs):
        context = super(UpdateGesturalEventView,self).get_context_data(**kwargs)
        return context


class DeleteGesturalEventView(DeleteView):
    model=GesturalEvent
    success_url = '/gbdb/index.html'


class GesturalEventDetailView(DetailView):
    model = GesturalEvent
    template_name = 'gbdb/gestural_event/gestural_event_view.html'

    def get_context_data(self, **kwargs):
        context = super(GesturalEventDetailView, self).get_context_data(**kwargs)
        context['ispopup']='_popup' in self.request.GET
        return context
