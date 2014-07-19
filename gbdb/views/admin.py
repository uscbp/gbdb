from django.http import HttpResponse, HttpResponseServerError
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render_to_response
from django.views.generic import UpdateView
from registration.backends.default.views import RegistrationView
from registration.models import User

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
