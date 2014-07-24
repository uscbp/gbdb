from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from gbdb.forms import PrimateForm
from gbdb.models import Primate

class EditPrimateMixin():
    model=Primate
    form_class=PrimateForm
    template_name='gbdb/primate/primate_detail.html'

class CreatePrimateView(EditPrimateMixin, CreateView):

    def get_context_data(self, **kwargs):
        context = super(CreatePrimateView,self).get_context_data(**kwargs)
        return context


class UpdatePrimateView(EditPrimateMixin,UpdateView):

    def get_context_data(self, **kwargs):
        context = super(UpdatePrimateView,self).get_context_data(**kwargs)
        return context


class DeletePrimateView(DeleteView):
    model=Primate
    success_url = '/gbdb/index.html'


class PrimateDetailView(DetailView):
    model = Primate
    template_name = 'gbdb/primate/primate_view.html'

    def get_context_data(self, **kwargs):
        context = super(PrimateDetailView, self).get_context_data(**kwargs)
        return context