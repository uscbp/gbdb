from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import BaseDeleteView
from django.contrib.sites.models import get_current_site
import os
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, FormView
from gbdb.forms import BehavioralEventForm, BehavioralEventSearchForm
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
        if self.request.is_ajax():
            context = self.get_context_data()
            data={'errors':{}}
            for key,value in form.errors.iteritems():
                data['errors'][key]=value
            return self.render_to_json_response(data, status=400)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        context = self.get_context_data()

        self.object = form.save(commit=False)

        data={
            'errors':{},
        }

        if self.object.parent is None or not context['allow_video']:
            if len(form.cleaned_data['start_time'])==0:
                data['errors']['start_time']=['Field required']
            if len(form.cleaned_data['duration'])==0:
                data['errors']['duration']=['Field required']

        if len(form.cleaned_data['contexts'])==0:
            data['errors']['contexts']=['Field required']
        if len(form.cleaned_data['ethograms'])==0:
            data['errors']['ethograms']=['Field required']

        if self.object.type=='gestural':
            if len(form.cleaned_data['goal_met'])==0:
                data['errors']['goal_met']=['Field required']
            if form.cleaned_data['signaller'] is None:
                data['errors']['signaller']=['Field required']
            if form.cleaned_data['recipient'] is None:
                data['errors']['recipient']=['Field required']
            if form.cleaned_data['gesture'] is None:
                data['errors']['gesture']=['Field required']

        if not 'start_time' in data['errors'] and not 'duration' in data['errors']:
            if self.object.parent is None:
                if self.object.observation_session.video.name:
                    if self.object.end_time()>self.object.observation_session.duration_seconds():
                        data['errors']['duration']=['Event exceeds observation session duration']
                    for other_event in BehavioralEvent.objects.filter(observation_session=self.object.observation_session,parent__isnull=True).exclude(id=self.object.id):
                        if other_event.start_time < self.object.end_time()<other_event.end_time() or other_event.start_time < self.object.start_time < other_event.end_time():
                            data['errors']['start_time']=['Event overlaps other events']
            else:
                if self.object.end_time()>self.object.parent.end_time():
                    data['errors']['duration']=['Subevent exceeds parent event duration']
                if self.object.start_time<self.object.parent.start_time:
                    data['errors']['start_time']=['Subevent starts before parent event']
                for other_event in BehavioralEvent.objects.filter(parent=self.object.parent).exclude(id=self.object.id):
                    if other_event.start_time < self.object.end_time()<other_event.end_time() or other_event.start_time < self.object.start_time < other_event.end_time():
                        data['errors']['start_time']=['Subevent overlaps other subevents']

        if len(data['errors'].keys()):
            return self.render_to_json_response(data, status=400)

        self.object.save()
        if self.object.type=='gestural':
            gestural_event=GesturalEvent(behavioralevent_ptr_id=self.object.pk)
            gestural_event.__dict__.update(self.object.__dict__)
            gestural_event.signaller=form.cleaned_data['signaller']
            gestural_event.recipient=form.cleaned_data['recipient']
            gestural_event.gesture=form.cleaned_data['gesture']
            gestural_event.recipient_response=form.cleaned_data['recipient_response']
            gestural_event.goal_met=form.cleaned_data['goal_met']
            gestural_event.save()
            self.object=gestural_event
            form.instance=gestural_event

        form.save_m2m()

        if self.object.type=='gestural':
            if not self.object.signaller in self.object.primates.all():
                self.object.primates.add(self.object.signaller)
            if not self.object.recipient in self.object.primates.all():
                self.object.primates.add(self.object.recipient)
            self.object.save()

        if self.object.parent is not None:
            for context in self.object.contexts.all():
                if not context in self.object.parent.contexts.all():
                    self.object.parent.contexts.add(context)
            for ethogram in self.object.ethograms.all():
                if not ethogram in self.object.parent.ethograms.all():
                    self.object.parent.ethograms.add(ethogram)
            for primate in self.object.primates.all():
                if not primate in self.object.parent.primates.all():
                    self.object.parent.primates.add(primate)

            self.object.parent.save()

        if self.request.is_ajax():
            data = {
                 'id': self.object.id,
                 'type': self.object.type,
                 'start_time': '',
                 'duration': '',
                 'end_time': self.object.end_time(),
                 'video': '/videos/behavioral_event/%d.mp4' % self.object.id,
                 'video_url_mp4': self.object.video_url_mp4(),
                 'contexts': ', '.join([context.name for context in self.object.contexts.all()]),
                 'ethograms': ', '.join([ethogram.name for ethogram in self.object.ethograms.all()]),
                 'primates': ', '.join([primate.__str__() for primate in self.object.primates.all()]),
                 'notes': self.object.notes,
                 'signaller': '',
                 'signaller_id': '',
                 'recipient': '',
                 'recipient_id': '',
                 'gesture': '',
                 'gesture_id': '',
                 'recipient_response': '',
                 'goal_met': '',
                 'subevents': []
            }

            if self.object.type=='gestural':
                data['signaller']=self.object.signaller.__str__()
                data['signaller_id']=self.object.signaller.id
                data['recipient']=self.object.recipient.__str__()
                data['recipient_id']=self.object.recipient.id
                data['gesture']=self.object.gesture.__str__()
                data['gesture_id']=self.object.gesture.id
                data['recipient_response']=self.object.recipient_response.__str__()
                data['goal_met']=self.object.goal_met.__str__()

            if not self.object.video.name:
                data['start_time']=float(self.object.start_time)
                data['duration']=float(self.object.duration)

            for event in BehavioralEvent.objects.filter(parent=self.object).order_by('start_time'):
                subevent_data={
                    'id': event.id,
                    'type': event.type,
                    'start_time': float(event.start_time),
                    'duration': float(event.duration),
                    'end_time': event.end_time(),
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
        if 'parent_event' in self.request.GET:
            initial['parent']=BehavioralEvent.objects.get(id=self.request.GET.get('parent_event'))
        initial['type']='generic'
        return initial

    def get_form(self, form_class):
        form=super(CreateBehavioralEventView,self).get_form(form_class)
        if 'parent' not in self.request.POST:
            observation_session=ObservationSession.objects.get(id=self.request.GET.get('observation_session'))
            if observation_session.video is None or not observation_session.video.name:
                form.fields['video'].required=True
        return form

    def get_context_data(self, **kwargs):
        context = super(CreateBehavioralEventView,self).get_context_data(**kwargs)
        context['allow_video']=False
        if 'parent_event' not in self.request.GET:
            observation_session=ObservationSession.objects.get(id=self.request.GET.get('observation_session'))
            if observation_session.video is None or not observation_session.video.name:
                context['allow_video']=True
        context['contexts']=Context.objects.all()
        context['ethograms']=Ethogram.objects.all()
        context['primates'] = Primate.objects.all()
        context['signallers'] = context['recipients'] = Primate.objects.all()
        context['gestures'] = Gesture.objects.all()
        return context


class UpdateBehavioralEventView(EditBehavioralEventMixin,UpdateView):

    def get_object(self, queryset=None):
        object=super(UpdateBehavioralEventView,self).get_object(queryset=queryset)
        if GesturalEvent.objects.filter(id=object.id):
            object=GesturalEvent.objects.get(id=object.id)
        return object

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
            if 'parentIdx' in self.request.POST:
                context['parentIdx']=self.request.POST['parentIdx']
        return context


class SearchBehavioralEventView(FormView):
    form_class=BehavioralEventSearchForm
    template_name='gbdb/behavioral_event/behavioral_event_search.html'

    def form_valid(self, form):
        context=self.get_context_data(form=form)
        user=self.request.user

        context['behavioral_events']=runBehavioralEventSearch(form.cleaned_data, user.id)

        return self.render_to_response(context)