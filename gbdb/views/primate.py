from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, FormView
from gbdb.forms import PrimateForm, PrimateSearchForm
from gbdb.models import Primate
from gbdb.search import runPrimateSearch

class EditPrimateMixin():
    model=Primate
    form_class=PrimateForm
    template_name='gbdb/primate/primate_detail.html'

    def form_valid(self, form):
        context = self.get_context_data()

        self.object = form.save(commit=False)
        self.object.save()
        form.save_m2m()

        url=self.get_success_url()
        if '_popup' in self.request.GET:
            url+='?_popup=1'
        return redirect(url)

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
        context['ispopup']='_popup' in self.request.GET
        return context


class SearchPrimateView(FormView):
    form_class=PrimateSearchForm
    template_name='gbdb/primate/primate_search.html'

    def form_valid(self, form):
        context=self.get_context_data(form=form)
        user=self.request.user

        context['primates']=runPrimateSearch(form.cleaned_data, user.id)

        return self.render_to_response(context)