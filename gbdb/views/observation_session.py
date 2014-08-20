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

class EditObservationSessionMixin():
    model=ObservationSession
    form_class=ObservationSessionForm
    template_name='gbdb/observation_session/observation_session_detail.html'

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
        return context


class UpdateObservationSessionView(EditObservationSessionMixin,UpdateView):

    def get_context_data(self, **kwargs):
        context = super(UpdateObservationSessionView,self).get_context_data(**kwargs)
        return context


class DeleteObservationSessionView(DeleteView):
    model=ObservationSession
    success_url = '/gbdb/index.html'


class ObservationSessionDetailView(DetailView):
    model = ObservationSession
    template_name = 'gbdb/observation_session/observation_session_view.html'

    def get_context_data(self, **kwargs):
        context = super(ObservationSessionDetailView, self).get_context_data(**kwargs)
        context['behavioral_events'] = BehavioralEvent.objects.filter(observation_session=self.object, parent__isnull=True)
        if self.object.video.name:
            root,ext=os.path.splitext(self.object.video.name)
            context['video_url_mp4'] = ''.join(['http://', get_current_site(self.request).domain, os.path.join('/media/','%s.mp4' % root)])
            context['video_url_ogg'] = ''.join(['http://', get_current_site(self.request).domain, os.path.join('/media/','%s.ogg' % root)])
            context['video_url_swf'] = ''.join(['http://', get_current_site(self.request).domain, os.path.join('/media/','%s.swf' % root)])
        return context


class SearchObservationSessionView(FormView):
    form_class=ObservationSessionSearchForm
    template_name='gbdb/observation_session/observation_session_search.html'

    def form_valid(self, form):
        context=self.get_context_data(form=form)
        user=self.request.user

        context['observation_sessions']=runObservationSessionSearch(form.cleaned_data, user.id)

        return self.render_to_response(context)