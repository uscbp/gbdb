from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from gbdb.forms import ObservationSessionForm, BehavioralEventFormSet
from gbdb.models import ObservationSession, BehavioralEvent

class EditObservationSessionMixin():
    model=ObservationSession
    form_class=ObservationSessionForm
    template_name='gbdb/observation_session/observation_session_detail.html'

    def form_valid(self, form):
        context = self.get_context_data()
        behavioral_event_formset = context['behavioral_event_formset']

        if behavioral_event_formset.is_valid():
            self.object = form.save(commit=False)
            # Set the collator if this is a new session
            if self.object.id is None:
                self.object.collator=self.request.user
            self.object.last_modified_by=self.request.user
            self.object.save()
            form.save_m2m()

            # save figures
            behavioral_event_formset.instance = self.object
            for behavioral_event_form in behavioral_event_formset.forms:
                if not behavioral_event_form in behavioral_event_formset.deleted_forms:
                    behavioral_event=behavioral_event_form.save(commit=False)
                    behavioral_event.observation_session=self.object
                    behavioral_event.save()

            # delete removed figures
            for behavioral_event_form in behavioral_event_formset.deleted_forms:
                if behavioral_event_form.instance.id:
                    behavioral_event_form.instance.delete()

            url=self.get_success_url()
            return redirect(url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class CreateObservationSessionView(EditObservationSessionMixin, CreateView):

    def get_context_data(self, **kwargs):
        context = super(CreateObservationSessionView,self).get_context_data(**kwargs)
        context['behavioral_event_formset']=BehavioralEventFormSet(self.request.POST or None, self.request.FILES or None,
            prefix='behavioral_event')
        return context


class UpdateObservationSessionView(EditObservationSessionMixin,UpdateView):

    def get_context_data(self, **kwargs):
        context = super(UpdateObservationSessionView,self).get_context_data(**kwargs)
        context['behavioral_event_formset']=BehavioralEventFormSet(self.request.POST or None, self.request.FILES or None,
            prefix='behavioral_event', instance=self.object,
            queryset=BehavioralEvent.objects.filter(observation_session=self.object))
        return context


class DeleteObservationSessionView(DeleteView):
    model=ObservationSession
    success_url = '/gbdb/index.html'


class ObservationSessionDetailView(DetailView):
    model = ObservationSession
    template_name = 'gbdb/observation_session/observation_session_view.html'

    def get_context_data(self, **kwargs):
        context = super(ObservationSessionDetailView, self).get_context_data(**kwargs)
        context['behavioral_events'] = BehavioralEvent.objects.filter(observation_session=self.object)
        return context