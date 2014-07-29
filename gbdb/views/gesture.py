from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from gbdb.forms import GestureForm
from gbdb.models import Gesture

class EditGestureMixin():
    model=Gesture
    form_class=GestureForm
    template_name='gbdb/gesture/gesture_detail.html'

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
        return context