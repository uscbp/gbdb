from django.http import HttpResponse, HttpResponseServerError
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render_to_response, render
from django.core.urlresolvers import reverse
from django.views.generic import UpdateView
from registration.backends.default.views import RegistrationView
from registration.models import User
from django.views.generic import UpdateView, View, CreateView, DetailView, ListView
from gbdb.models import CoWoGroup
from gbdb.forms import GroupForm
from uscbp.views import JSONResponseMixin
from django.views.generic.edit import BaseUpdateView
from guardian.shortcuts import assign_perm, remove_perm, get_perms

@login_required
def logout_view(request):
    # perform logout
    logout(request)
    # redirect to index
    return render_to_response('registration/logout.html')


# check if a username is unique
def username_available(request):
    # if ajax request and username provided
    if request.is_ajax() and 'username' in request.POST:
        username_str = request.POST['username']
        # return response if username is unique
        if not User.objects.filter(username=username_str).count():
            return HttpResponse(username_str)
        # return error if already taken
        else:
            return HttpResponseServerError(username_str)
    return HttpResponseServerError("Requires a username field.")


class GbdbRegistrationView(RegistrationView):

    def get_context_data(self, **kwargs):
        context=super(RegistrationView,self).get_context_data(**kwargs)
        return context

    #add user permissions here
    def form_valid(self, request, form):
        new_user = self.register(request, **form.cleaned_data)
        new_user.first_name=request.POST['first_name']
        new_user.last_name=request.POST['last_name']
        new_user.save()
        success_url = self.get_success_url(request, new_user)

        # success_url may be a simple string, or a tuple providing the
        # full argument set for redirect(). Attempting to unpack it
        # tells us which one it is.
        try:
            to, args, kwargs = success_url
            return redirect(to, *args, **kwargs)
        except ValueError:
            return redirect(success_url)
    

class AdminDetailView(ListView):
    template_name ='gbdb/admin/admin.html'
    model = CoWoGroup
    
    def get_context_data(self, **kwargs):
        context = super(AdminDetailView,self).get_context_data(**kwargs)
        context['user_admin_permissions']={}
        context['groups']=CoWoGroup.objects.filter(members__id = self.request.user.id).order_by('name')
        for group in context['groups']:
            context['user_admin_permissions'][group]=self.request.user.has_perm('gbdb.admin_cowogroup', group)

        return context

        
class CreateGroupView(CreateView):
    model = CoWoGroup
    form_class = GroupForm
    template_name = 'gbdb/admin/group_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CreateGroupView,self).get_context_data(**kwargs)
        
        context['user_admin_permissions']={}
        context['members']=[self.request.user]
        for user in context['members']:
            context['user_admin_permissions'][user]=False
            if self.request.POST:
                context['user_admin_permissions'][user]=('user-%d_admin' % user.id) in self.request.POST
            else:
                context['user_admin_permissions'][user]=user.has_perm('gbdb.admin_cowogroup',self.object)
                
        context['ispopup']=('_popup' in self.request.GET)
        return context

    def form_valid(self, form):
        context = self.get_context_data()

        group=form.save()
        
        assign_perm('gbdb.admin_cowogroup', self.request.user, group)

#         for permission in gbdb_permissions:
#             if context[permission]:
#                 assign_perm(permission, group)
#             else:
#                 remove_perm(permission, group)

        redirect_url='%s?action=add' % reverse('group_view', kwargs={'pk': group.id})
        if context['ispopup']:
            redirect_url+='&_popup=1'
        return redirect(redirect_url)


class UpdateGroupView(UpdateView):
    model = CoWoGroup
    form_class = GroupForm
    template_name = 'gbdb/admin/group_detail.html'

    def get_context_data(self, **kwargs):
        context = super(UpdateGroupView,self).get_context_data(**kwargs)
#         if self.request.POST:
#             for permission in gbdb_permissions:
#                 context[permission]=permission in self.request.POST
#         else:
#             for permission in gbdb_permissions:
#                 context[permission]=self.object.permissions.filter(id=Permission.objects.get(codename=permission).id)
        context['ispopup']=('_popup' in self.request.GET)
        
        context['user_admin_permissions']={}
        context['members']=self.object.members.all()
        for user in context['members']:
            context['user_admin_permissions'][user]=False
            if self.request.POST:
                context['user_admin_permissions'][user]=('user-%d_admin' % user.id) in self.request.POST
            else:
                context['user_admin_permissions'][user]=user.has_perm('gbdb.admin_cowogroup',self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()

        group=form.save()
        
        for user in context['members']:
            if context['user_admin_permissions'][user]:
                assign_perm('admin_cowogroup', user, self.object)
            else:
                remove_perm('admin_cowogroup', user, self.object)

#         for permission in gbdb_permissions:
#             if context[permission]:
#                 assign_perm(permission, group)
#             else:
#                 remove_perm(permission, group)

        redirect_url='%s?action=edit' % reverse('group_view', kwargs={'pk': group.id})
        if context['ispopup']:
            redirect_url+='&_popup=1'
        return redirect(redirect_url)


class GroupDetailView(DetailView):
    model = CoWoGroup
    template_name = 'gbdb/admin/group_view.html'

    def get_context_data(self, **kwargs):
        context = super(GroupDetailView,self).get_context_data(**kwargs)
        context['ispopup']=('_popup' in self.request.GET)
        context['name']=self.object.name
        #context['administrators']=self.object.administrators.all()
        context['user_admin_permissions']={}
        context['members']=self.object.members.all()
        for user in context['members']:
            context['user_admin_permissions'][user]=user.has_perm('gbdb.admin_cowogroup',self.object)
        context['id']=self.object.id
        context['isadmin']= self.request.user.has_perm('gbdb.admin_cowogroup',self.object)
        #for permission in gbdb_permissions:
        #    context[permission]=self.object.permissions.filter(id=Permission.objects.get(codename=permission).id)
        return context


class DeleteGroupView(JSONResponseMixin,BaseUpdateView):
    model = CoWoGroup

    def get_context_data(self, **kwargs):
        context={'msg':u'No POST data sent.' }
        if self.request.is_ajax():
            # load group
            group=CoWoGroup.objects.get(id=self.kwargs.get('pk', None))

            # remove users
            related_users=User.objects.filter(groups__id=self.request.POST['id'])
            for user in related_users:
                user.groups.remove(group)
                user.save()

            # delete group
            group.delete()
            context = {'id': self.request.POST['id']}
        return context
        
