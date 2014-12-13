from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, FormView
from gbdb.forms import GestureForm, GestureSearchForm
from gbdb.models import Gesture
from gbdb.search import runGestureSearch

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
        return context


class SearchGestureView(FormView):
    form_class=GestureSearchForm
    template_name='gbdb/gesture/gesture_search.html'

    def form_valid(self, form):
        context=self.get_context_data(form=form)
        user=self.request.user

        context['gestures']=runGestureSearch(form.cleaned_data, user.id)

        return self.render_to_response(context)