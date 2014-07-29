from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView
from gbdb.forms import BehavioralEventForm
from gbdb.models import BehavioralEvent, ObservationSession

class EditBehavioralEventMixin():
    model=BehavioralEvent
    form_class=BehavioralEventForm
    template_name='gbdb/behavioral_event/behavioral_event_detail.html'

    def form_valid(self, form):
        context = self.get_context_data()

        self.object = form.save(commit=False)
        # Set the collator if this is a new session
        if self.object.id is None:
            self.object.collator=self.request.user
        self.object.last_modified_by=self.request.user
        self.object.save()
        form.save_m2m()

        url=self.get_success_url()
        if '_popup' in self.request.GET:
            url+='?_popup=1'
        return redirect(url)


class CreateBehavioralEventView(EditBehavioralEventMixin, CreateView):

    def get_initial(self):
        initial = super(CreateBehavioralEventView,self).get_initial()
        initial['observation_session']=ObservationSession.objects.get(id=self.request.GET.get('observation_session'))
        return initial

    def get_context_data(self, **kwargs):
        context = super(CreateBehavioralEventView,self).get_context_data(**kwargs)
        return context


class UpdateBehavioralEventView(EditBehavioralEventMixin,UpdateView):

    def get_context_data(self, **kwargs):
        context = super(UpdateBehavioralEventView,self).get_context_data(**kwargs)
        return context


class DeleteBehavioralEventView(DeleteView):
    model=BehavioralEvent
    success_url = '/gbdb/index.html'


class BehavioralEventDetailView(DetailView):
    model = BehavioralEvent
    template_name = 'gbdb/behavioral_event/behavioral_event_view.html'

    def get_context_data(self, **kwargs):
        context = super(BehavioralEventDetailView, self).get_context_data(**kwargs)
        context['ispopup']='_popup' in self.request.GET
        return context
