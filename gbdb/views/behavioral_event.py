from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView
from gbdb.forms import BehavioralEventForm, SubBehavioralEventFormSet, GesturalEventFormSet
from gbdb.models import BehavioralEvent, ObservationSession, GesturalEvent, Context, Ethogram, Primate, Gesture

class EditBehavioralEventMixin():
    model=BehavioralEvent
    form_class=BehavioralEventForm
    template_name='gbdb/behavioral_event/behavioral_event_detail.html'

    def form_valid(self, form):
        context = self.get_context_data()
        sub_behavioral_event_formset = context['sub_behavioral_event_formset']
        sub_gestural_event_formset = context['sub_gestural_event_formset']

        if sub_behavioral_event_formset.is_valid() and sub_gestural_event_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.save()
            form.save_m2m()

            # save sub-events
            sub_behavioral_event_formset.instance = self.object
            for sub_behavioral_event_form in sub_behavioral_event_formset.forms:
                if not sub_behavioral_event_form in sub_behavioral_event_formset.deleted_forms:
                    behavioral_event=sub_behavioral_event_form.save(commit=False)
                    behavioral_event.parent=self.object
                    behavioral_event.observation_session=self.object.observation_session
                    behavioral_event.save()
                    sub_behavioral_event_form.save_m2m()

            # delete removed sub-events
            for sub_behavioral_event_form in sub_behavioral_event_formset.deleted_forms:
                if sub_behavioral_event_form.instance.id:
                    sub_behavioral_event_form.instance.delete()

            sub_gestural_event_formset.instance=self.object
            for sub_gestural_event_form in sub_gestural_event_formset.forms:
                if not sub_gestural_event_form in sub_gestural_event_formset.deleted_forms:
                    gestural_event=sub_gestural_event_form.save(commit=False)
                    gestural_event.parent=self.object
                    gestural_event.observation_session=self.object.observation_session
                    gestural_event.save()
                    sub_gestural_event_form.save_m2m()

            for sub_gestural_event_form in sub_gestural_event_formset.deleted_forms:
                if sub_gestural_event_form.instance.id:
                    sub_gestural_event_form.instance.delete()

            url=self.get_success_url()
            if '_popup' in self.request.GET:
                url+='?_popup=1'
            return redirect(url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class CreateBehavioralEventView(EditBehavioralEventMixin, CreateView):

    def get_initial(self):
        initial = super(CreateBehavioralEventView,self).get_initial()
        initial['observation_session']=ObservationSession.objects.get(id=self.request.GET.get('observation_session'))
        return initial

    def get_context_data(self, **kwargs):
        context = super(CreateBehavioralEventView,self).get_context_data(**kwargs)
        context['contexts']=Context.objects.all()
        context['ethograms']=Ethogram.objects.all()
        context['sub_behavioral_event_formset']=SubBehavioralEventFormSet(self.request.POST or None, self.request.FILES or None,
            prefix='sub_behavioral_event')
        context['sub_gestural_event_formset']=GesturalEventFormSet(self.request.POST or None, self.request.FILES or None,
            prefix='sub_gestural_event')
        context['primates'] = Primate.objects.all()
        context['signallers'] = context['recipients'] = Primate.objects.all()
        context['gestures'] = Gesture.objects.all()
        return context


class UpdateBehavioralEventView(EditBehavioralEventMixin,UpdateView):

    def get_context_data(self, **kwargs):
        context = super(UpdateBehavioralEventView,self).get_context_data(**kwargs)
        context['contexts']=Context.objects.all()
        context['ethograms']=Ethogram.objects.all()
        context['sub_behavioral_event_formset']=SubBehavioralEventFormSet(self.request.POST or None, self.request.FILES or None,
            prefix='sub_behavioral_event', instance=self.object,
            queryset=BehavioralEvent.objects.filter(parent=self.object))
        context['sub_gestural_event_formset']=GesturalEventFormSet(self.request.POST or None, self.request.FILES or None,
            prefix='sub_gestural_event', instance=self.object,
            queryset=GesturalEvent.objects.filter(parent=self.object))
        context['primates'] = Primate.objects.all()
        context['signallers'] = context['recipients'] = Primate.objects.all()
        context['gestures'] = Gesture.objects.all()
        return context


class DeleteBehavioralEventView(DeleteView):
    model=BehavioralEvent
    success_url = '/gbdb/index.html'


class BehavioralEventDetailView(DetailView):
    model = BehavioralEvent
    template_name = 'gbdb/behavioral_event/behavioral_event_view.html'

    def get_context_data(self, **kwargs):
        context = super(BehavioralEventDetailView, self).get_context_data(**kwargs)
        context['sub_behavioral_events']=BehavioralEvent.objects.filter(parent=self.object,gesturalevent__isnull=True)
        context['sub_gestural_events']=GesturalEvent.objects.filter(parent=self.object)
        context['ispopup']='_popup' in self.request.GET
        return context
