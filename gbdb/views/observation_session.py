import os
from django.contrib.sites.models import get_current_site
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import request
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, FormView
from gbdb.forms import ObservationSessionForm, ObservationSessionSearchForm
from gbdb.models import ObservationSession, BehavioralEvent, GesturalEvent
from gbdb.search import runObservationSessionSearch
from guardian.shortcuts import assign_perm, remove_perm, get_perms
import json
from django.http import HttpResponse
from guardian.mixins import PermissionRequiredMixin
from registration.models import User
from django.contrib.auth.models import Group

class EditObservationSessionMixin():
    model=ObservationSession
    form_class=ObservationSessionForm
    template_name='gbdb/observation_session/observation_session_detail.html'
    
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)
    
    def form_invalid(self, form):
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # Set the collator if this is a new session
        if self.object.id is None:
            self.object.collator=self.request.user
        self.object.last_modified_by=self.request.user
        self.object.save()
        form.save_m2m()

        if self.request.is_ajax():
            data = {
                'id': self.object.id,
            }
            return self.render_to_json_response(data)
        else:
            url=self.get_success_url()
            return redirect(url)


#assign permissions to collator
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


class ObservationSessionDetailView(PermissionRequiredMixin, DetailView):
    model = ObservationSession
    template_name = 'gbdb/observation_session/observation_session_view.html'
    permission_required = 'gbdb.view_observationsession'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(ObservationSessionDetailView, self).get_context_data(**kwargs)
        event_list = []
        behavioral_events = BehavioralEvent.objects.filter(observation_session=self.object, parent__isnull=True).order_by('start_time');
        for behavioral_event in behavioral_events:
            sub_events=[]
            for sub_event in BehavioralEvent.objects.filter(parent=behavioral_event).order_by('start_time'):
                if GesturalEvent.objects.filter(id=sub_event.id).count():
                    sub_events.append(GesturalEvent.objects.get(id=sub_event.id))
                else:
                    sub_events.append(sub_event)
            event_list.append([behavioral_event, sub_events])
        context['behavioral_events'] = event_list
        context['site_url']='http://%s' % get_current_site(self.request)
        context['timeline']=self.object
        
        #context['has_edit_perms'] = self.request.user.has_perm('gbdb.edit', self.object)
        #context['has_delete_perms'] = self.request.user.has_perm('delete', self.object)
        
        context['has_delete_perms'] = self.request.user.has_perm('gbdb.delete_observationsession', self.object)
        context['has_edit_perms'] = self.request.user.has_perm('gbdb.edit_observationsession', self.object)
        
        return context


class SearchObservationSessionView(FormView):
    form_class=ObservationSessionSearchForm
    template_name='gbdb/observation_session/observation_session_search.html'

    def form_valid(self, form):
        context=self.get_context_data(form=form)
        user=self.request.user

        context['observation_sessions']=runObservationSessionSearch(form.cleaned_data, user.id)

        return self.render_to_response(context)
    

class ManageObservationSessionPermissionsView(DetailView):
    template_name = 'gbdb/observation_session_permissions_detail.html'

    def post(self, request, *args, **kwargs):
        self.object=ObservationSession.objects.get(id=self.kwargs.get('pk',None))
        context = self.get_context_data(**kwargs)
        for user in context['users']:
            if context['user_view_permissions'][user]:
                assign_perm('view_observationsession', user, self.object)
            else:
                remove_perm('view_observationsession', user, self.object)
            if context['user_manage_permissions'][user]:
                assign_perm('manage_observationsession', user, self.object)
            else:
                remove_perm('manage_observationsession', user, self.object)
            if context['user_edit_permissions'][user]:
                assign_perm('edit_observationsession', user, self.object)
            else:
                remove_perm('edit_observationsession', user, self.object)
            if context['user_delete_permissions'][user]:
                assign_perm('delete_observationsession', user, self.object)
            else:
                remove_perm('delete_observationsession', user, self.object)
        for group in context['groups']:
            if context['group_view_permissions'][group]:
                assign_perm('view_observationsession', group, self.object)
            else:
                remove_perm('view_observationsession', group, self.object)
            if context['group_manage_permissions'][group]:
                assign_perm('manage_observationsession', group, self.object)
            else:
                remove_perm('manage_observationsession', group, self.object)
            if context['group_edit_permissions'][group]:
                assign_perm('edit_observationsession', group, self.object)
            else:
                remove_perm('edit_observationsession', group, self.object)
            if context['group_delete_permissions'][group]:
                assign_perm('delete_observationsession', group, self.object)
            else:
                remove_perm('delete_observationsession', group, self.object)

        redirect_url='/gbdb/observation_session/%d/permissions/' % self.object.id
        if context['ispopup']:
            redirect_url+='?_popup=1'
        return redirect(redirect_url)

    def get(self, request, *args, **kwargs):
        self.object=ObservationSession.objects.get(id=self.kwargs.get('pk',None))
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context=super(DetailView,self).get_context_data(**kwargs)
        context['observation_session']=self.object
        context['helpPage']='permissions.html#individual-entry-permissions'
        context['users']=User.objects.all().exclude(id=self.request.user.id)
        context['groups']=Group.objects.filter(user__id=self.request.user.id)
        context['ispopup']=('_popup' in self.request.GET)
        context['user_view_permissions']={}
        context['user_manage_permissions']={}
        context['user_edit_permissions']={}
        context['user_delete_permissions']={}
        context['group_view_permissions']={}
        context['group_manage_permissions']={}
        context['group_edit_permissions']={}
        context['group_delete_permissions']={}
        for user in context['users']:
            context['user_view_permissions'][user]=False
            context['user_manage_permissions'][user]=False
            context['user_edit_permissions'][user]=False
            context['user_delete_permissions'][user]=False
            if self.request.POST:
                context['user_view_permissions'][user]=('user-%d_view' % user.id) in self.request.POST
                context['user_manage_permissions'][user]=('user-%d_manage' % user.id) in self.request.POST
                context['user_edit_permissions'][user]=('user-%d_edit' % user.id) in self.request.POST
                context['user_delete_permissions'][user]=('user-%d_delete' % user.id) in self.request.POST
            else:
                context['user_view_permissions'][user]=user.has_perm('view_observationsession',self.object)
                context['user_manage_permissions'][user]=user.has_perm('manage_observationsession',self.object)
                context['user_edit_permissions'][user]=user.has_perm('edit_observationsession',self.object)
                context['user_delete_permissions'][user]=user.has_perm('delete_observationsession',self.object)
        for group in context['groups']:
            context['group_view_permissions'][group]=False
            context['group_manage_permissions'][group]=False
            context['group_edit_permissions'][group]=False
            context['group_delete_permissions'][group]=False
            if self.request.POST:
                context['group_view_permissions'][group]=('group-%d_view' % group.id) in self.request.POST
                context['group_manage_permissions'][group]=('group-%d_manage' % group.id) in self.request.POST
                context['group_edit_permissions'][group]=('group-%d_edit' % group.id) in self.request.POST
                context['group_delete_permissions'][group]=('group-%d_delete' % group.id) in self.request.POST
            else:
                context['group_view_permissions'][group]='view_observationsession' in get_perms(group,self.object)
                context['group_manage_permissions'][group]='manage_observationsession' in get_perms(group,self.object)
                context['group_edit_permissions'][group]='edit_observationsession' in get_perms(group,self.object)
                context['group_delete_permissions'][group]='delete_observationsession' in get_perms(group,self.object)
        return context