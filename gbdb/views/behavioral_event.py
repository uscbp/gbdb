from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import BaseDeleteView
from django.contrib.sites.models import get_current_site
import os
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, FormView
from gbdb.forms import BehavioralEventForm, SubBehavioralEventFormSet, GesturalEventFormSet, BehavioralEventSearchForm
from gbdb.models import BehavioralEvent, ObservationSession, GesturalEvent, Context, Ethogram, Primate, Gesture
from gbdb.search import runBehavioralEventSearch
import json
from django.http import HttpResponse
from uscbp.views import JSONResponseMixin

class EditBehavioralEventMixin(object):
    model=BehavioralEvent
    form_class=BehavioralEventForm
    template_name='gbdb/behavioral_event/behavioral_event_detail.html'
    
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)
    
    def form_invalid(self, form):
        response = super(EditBehavioralEventMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

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

            if self.request.is_ajax():
                data = {
                     'id': self.object.id,
                     'start_time': '',
                     'duration': '',
                     'start_time_seconds': self.object.start_time_seconds(),
                     'end_time_seconds': self.object.end_time_seconds(),
                     'video': '/videos/behavioral_event/%d.mp4' % self.object.id,
                     'video_url_mp4': self.object.video_url_mp4(),
                     'primates': ', '.join([primate.__str__() for primate in self.object.primates.all()]),
                     'contexts': ', '.join([context.name for context in self.object.contexts.all()]),
                     'ethograms': ', '.join([ethogram.name for ethogram in self.object.ethograms.all()]),
                     'notes': self.object.notes,
                     'subevents': []
                }

                if self.object.start_time:
                    data['start_time']='%d:%d:%d.%d' % (self.object.start_time.hour,self.object.start_time.minute,
                                                        self.object.start_time.second,self.object.start_time.microsecond)
                if self.object.duration:
                    data['duration']='%d:%d:%d.%d' % (self.object.duration.hour,self.object.duration.minute,
                                                      self.object.duration.second,self.object.duration.microsecond)

                for event in BehavioralEvent.objects.filter(parent=self.object).order_by('start_time'):
                    subevent_data={
                        'id': event.id,
                        'type': event.type,
                        'start_time': '%d:%d:%d.%d' % (event.start_time.hour,event.start_time.minute,
                                                       event.start_time.second,event.start_time.microsecond),
                        'relative_to': event.relative_to,
                        'duration': '%d:%d:%d.%d' % (event.duration.hour,event.duration.minute,
                                                     event.duration.second,event.duration.microsecond),
                        'start_time_seconds': event.start_time_seconds(),
                        'end_time_seconds': event.end_time_seconds(),
                        'primates': ', '.join([primate.__str__() for primate in event.primates.all()]),
                        'contexts': ', '.join([context.name for context in event.contexts.all()]),
                        'ethograms': ', '.join([ethogram.name for ethogram in event.ethograms.all()]),
                        'notes': event.notes,
                        'signaller_id': '',
                        'signaller': '',
                        'recipient_id': '',
                        'recipient': '',
                        'gesture_id': '',
                        'gesture': '',
                        'recipient_response': '',
                        'goal_met': ''
                    }
                    if GesturalEvent.objects.filter(id=event.id).count():
                        gestural_event=GesturalEvent.objects.get(id=event.id)
                        subevent_data['signaller_id']=gestural_event.signaller.id
                        subevent_data['signaller']=gestural_event.signaller.__str__()
                        subevent_data['recipient_id']=gestural_event.recipient.id
                        subevent_data['recipient']=gestural_event.recipient.__str__()
                        if gestural_event.gesture is not None:
                            subevent_data['gesture_id']=gestural_event.gesture.id
                            subevent_data['gesture']=gestural_event.gesture.name
                        subevent_data['recipient_response']=gestural_event.recipient_response
                        subevent_data['goal_met']=gestural_event.goal_met
                    data['subevents'].append(subevent_data)

                return self.render_to_json_response(data)

            url=self.get_success_url()
            if '_popup' in self.request.GET:
                url+='?_popup=1'
                return redirect(self.object.observation_session.get_absolute_url())
            else:
                return self.render_to_response(self.get_context_data(form=form))


class CreateBehavioralEventView(EditBehavioralEventMixin, CreateView):

    def get_initial(self):
        initial = super(CreateBehavioralEventView,self).get_initial()
        initial['observation_session']=ObservationSession.objects.get(id=self.request.GET.get('observation_session'))
        initial['type']='generic'
        return initial

    def get_form(self, form_class):
        form=super(CreateBehavioralEventView,self).get_form(form_class)
        observation_session=ObservationSession.objects.get(id=self.request.GET.get('observation_session'))
        if observation_session.video is None or not observation_session.video.name:
            form.fields['video'].required=True
        return form

    def get_context_data(self, **kwargs):
        context = super(CreateBehavioralEventView,self).get_context_data(**kwargs)
        context['allow_video']=False
        observation_session=ObservationSession.objects.get(id=self.request.GET.get('observation_session'))
        if observation_session.video is None or not observation_session.video.name:
            context['allow_video']=True
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

    def get_form(self, form_class):
        form=super(UpdateBehavioralEventView,self).get_form(form_class)
        if self.object.parent is None:
            observation_session=ObservationSession.objects.get(id=self.object.observation_session.id)
            if observation_session.video is None or not observation_session.video.name:
                form.fields['video'].required=True
        return form

    def get_context_data(self, **kwargs):
        context = super(UpdateBehavioralEventView,self).get_context_data(**kwargs)
        context['allow_video']=False
        if self.object.parent is None:
            observation_session=ObservationSession.objects.get(id=self.object.observation_session.id)
            if observation_session.video is None or not observation_session.video.name:
                context['allow_video']=True
        context['contexts']=Context.objects.all()
        context['ethograms']=Ethogram.objects.all()
        context['sub_behavioral_event_formset']=SubBehavioralEventFormSet(self.request.POST or None, self.request.FILES or None,
            prefix='sub_behavioral_event', instance=self.object,
            queryset=BehavioralEvent.objects.filter(parent=self.object,gesturalevent__isnull=True))
        context['sub_gestural_event_formset']=GesturalEventFormSet(self.request.POST or None, self.request.FILES or None,
            prefix='sub_gestural_event', instance=self.object,
            queryset=GesturalEvent.objects.filter(parent=self.object))
        context['primates'] = Primate.objects.all()
        context['signallers'] = context['recipients'] = Primate.objects.all()
        context['gestures'] = Gesture.objects.all()
        return context


class DeleteBehavioralEventView(JSONResponseMixin,BaseDetailView):
    model=BehavioralEvent

    def get_context_data(self, **kwargs):
        context={'msg':u'No POST data sent.' }
        if self.request.is_ajax():
            self.object=self.get_object()
            self.object.delete()
            context={'idx': self.request.POST['idx']}
        return context


class BehavioralEventDetailView(DetailView):
    model = BehavioralEvent
    template_name = 'gbdb/behavioral_event/behavioral_event_view.html'

    def get_context_data(self, **kwargs):
        context = super(BehavioralEventDetailView, self).get_context_data(**kwargs)
        context['sub_behavioral_events']=BehavioralEvent.objects.filter(parent=self.object,gesturalevent__isnull=True)
        context['sub_gestural_events']=GesturalEvent.objects.filter(parent=self.object)
        context['ispopup']='_popup' in self.request.GET
        root,ext=os.path.splitext(self.object.video.name)
        context['video_url_mp4'] = ''.join(['http://', get_current_site(self.request).domain, os.path.join('/media/','%s.mp4' % root)])
        #context['video_url_ogg'] = ''.join(['http://', get_current_site(self.request).domain, os.path.join('/media/','%s.ogg' % root)])
        #context['video_url_swf'] = ''.join(['http://', get_current_site(self.request).domain, os.path.join('/media/','%s.swf' % root)])
        return context


class SearchBehavioralEventView(FormView):
    form_class=BehavioralEventSearchForm
    template_name='gbdb/behavioral_event/behavioral_event_search.html'

    def form_valid(self, form):
        context=self.get_context_data(form=form)
        user=self.request.user

        context['behavioral_events']=runBehavioralEventSearch(form.cleaned_data, user.id)

        return self.render_to_response(context)