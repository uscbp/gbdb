import os
from django.contrib.sites.models import get_current_site
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import request
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, FormView
from gbdb.forms import ObservationSessionForm, ObservationSessionSearchForm
from gbdb.models import ObservationSession, BehavioralEvent
from gbdb.search import runObservationSessionSearch
from timelinejs.views import JSONResponseMixin
import json
from django.http import HttpResponse

class EditObservationSessionMixin():
    model=ObservationSession
    form_class=ObservationSessionForm
    template_name='gbdb/observation_session/observation_session_detail.html'
    
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)
    
    def form_invalid(self, form):
        response = super(EditObservationSessionMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        
        if self.request.is_ajax():
            self.object = form.save();
            data = {
#                 'pk': self.object.pk,
#                 'start_time': self.object.start_time,
#                 'duration': self.object.duration,
            }
            return self.render_to_json_response(data)

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
        return redirect(url)


class CreateObservationSessionView(EditObservationSessionMixin, CreateView):

    def get_context_data(self, **kwargs):
        context = super(CreateObservationSessionView,self).get_context_data(**kwargs)
        context['template_ext'] = 'base_generic.html'
        return context


class UpdateObservationSessionView(EditObservationSessionMixin,UpdateView):

    def get_context_data(self, **kwargs):
        context = super(UpdateObservationSessionView,self).get_context_data(**kwargs)
        context['template_ext'] = 'empty_base.html'
        return context


class DeleteObservationSessionView(DeleteView):
    model=ObservationSession
    success_url = '/gbdb/index.html'


class ObservationSessionDetailView(DetailView):
    model = ObservationSession
    template_name = 'gbdb/observation_session/observation_session_view.html'

    def get_context_data(self, **kwargs):
        context = super(ObservationSessionDetailView, self).get_context_data(**kwargs)
        event_list = []
        behavioral_events = BehavioralEvent.objects.filter(observation_session=self.object, parent__isnull=True).order_by('start_time');
        for behavioral_event in behavioral_events:
            event_list.append([behavioral_event, BehavioralEvent.objects.filter(parent=behavioral_event).order_by('start_time')])
        #context['behavioral_events'] = BehavioralEvent.objects.filter(observation_session=self.object, parent__isnull=True)
        context['behavioral_events'] = event_list
        context['site_url']='http://%s' % get_current_site(self.request)
        context['timeline']=self.object
        return context


class SearchObservationSessionView(FormView):
    form_class=ObservationSessionSearchForm
    template_name='gbdb/observation_session/observation_session_search.html'

    def form_valid(self, form):
        context=self.get_context_data(form=form)
        user=self.request.user

        context['observation_sessions']=runObservationSessionSearch(form.cleaned_data, user.id)

        return self.render_to_response(context)