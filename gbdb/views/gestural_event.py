from django.contrib.sites.models import get_current_site
import os
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
        if not self.object.recipient in self.object.primates.all() or not self.object.signaller in self.object.primates.all():
            self.object.primates.clear()
            self.object.primates.add(self.object.recipient)
            self.object.primates.add(self.object.signaller)
            self.object.save()

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
        if self.object.video.name:
            root,ext=os.path.splitext(self.object.video.name)
            context['video_url_mp4'] = ''.join(['http://', get_current_site(self.request).domain, os.path.join('/media/','%s.mp4' % root)])
            context['video_url_ogg'] = ''.join(['http://', get_current_site(self.request).domain, os.path.join('/media/','%s.ogg' % root)])
            context['video_url_swf'] = ''.join(['http://', get_current_site(self.request).domain, os.path.join('/media/','%s.swf' % root)])
        else:
            file_root=os.path.join('videos','behavioral_event')
            context['video_url_mp4'] = ''.join(['http://', get_current_site(self.request).domain, os.path.join('/media',file_root,'%d.mp4' % self.object.id)])
            context['video_url_ogg'] = ''.join(['http://', get_current_site(self.request).domain, os.path.join('/media',file_root,'%d.ogg' % self.object.id)])
            context['video_url_swf'] = ''.join(['http://', get_current_site(self.request).domain, os.path.join('/media',file_root,'%d.swf' % self.object.id)])
        return context
