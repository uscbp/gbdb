from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from gbdb.forms import GestureForm
from gbdb.models import Gesture

class EditGestureMixin():
    model=Gesture
    form_class=GestureForm
    template_name='gbdb/gesture/gesture_detail.html'

    def form_valid(self, form):
        context = self.get_context_data()

        self.object = form.save(commit=False)
        self.object.save()
        form.save_m2m()

        url=self.get_success_url()
        if '_popup' in self.request.GET:
            url+='?_popup=1'
            if 'gestural_event_idx' in self.request.GET:
                url+='&gestural_event_idx='+self.request.GET['gestural_event_idx']
        return redirect(url)

class CreateGestureView(EditGestureMixin, CreateView):

    def get_context_data(self, **kwargs):
        context = super(CreateGestureView,self).get_context_data(**kwargs)
        return context


class UpdateGestureView(EditGestureMixin,UpdateView):

    def get_context_data(self, **kwargs):
        context = super(UpdateGestureView,self).get_context_data(**kwargs)
        return context


class DeleteGestureView(DeleteView):
    model=Gesture
    success_url = '/gbdb/index.html'


class GestureDetailView(DetailView):
    model = Gesture
    template_name = 'gbdb/gesture/gesture_view.html'

    def get_context_data(self, **kwargs):
        context = super(GestureDetailView, self).get_context_data(**kwargs)
        context['ispopup']='_popup' in self.request.GET
        if context['ispopup'] and 'gestural_event_idx' in self.request.GET:
            context['gestural_event_idx']=self.request.GET['gestural_event_idx']
        return context