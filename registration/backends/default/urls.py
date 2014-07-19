"""
URLconf for registration and activation, using django-registration's
default backend.

If the default behavior of these views is acceptable to you, simply
use a line like this in your root URLconf to set up the default URLs
for registration::

    (r'^accounts/', include('registration.backends.default.urls')),

This will also automatically set up the views in
``django.contrib.auth`` at sensible default locations.

If you'd like to customize registration behavior, feel free to set up
your own URL patterns for these views instead.

"""


from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url
from django.views.generic.base import TemplateView
from gbdb.forms import GbdbRegistrationForm

from django.contrib.auth import views as auth_views
from registration.backends.default.views import ActivationView
from registration.backends.default.views import RegistrationView


urlpatterns = patterns('',
                       url(r'^activate/complete/$',
                           TemplateView.as_view(template_name='registration/activation_complete.html'),
                           name='registration_activation_complete'),
                       # Activation keys get matched by \w+ instead of the more specific
                       # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
                       # that way it can return a sensible "inv
                       # alid key" message instead of a
                       # confusing 404.
                       url(r'^activate/(?P<activation_key>\w+)/$',
                           ActivationView.as_view(),
                           name='registration_activate'),
                       url(r'^register/$',
                           RegistrationView.as_view(form_class=GbdbRegistrationForm),
                           name='registration_register'),
                       url(r'^register/complete/$',
                           TemplateView.as_view(template_name='registration/registration_complete.html'),
                           name='registration_complete'),
                       url(r'^register/closed/$',
                           TemplateView.as_view(template_name='registration/registration_closed.html'),
                           name='registration_disallowed'),
                        url(r'^password/reset/$',
                            auth_views.password_reset,
                            name='auth_password_reset'),
                        url(r'^password/reset/confirm/uidb36/(?P<uidb36>.+)/token/(?P<token>.+)/$',
                            auth_views.password_reset_confirm,
                            name='django.contrib.auth.views.password_reset_confirm'),
                        url(r'^password/reset/done/$',
                            auth_views.password_reset_done,
                            name='password_reset_done'),
                        url(r'^password/reset/complete/$',
                            auth_views.password_reset_complete,
                            name='django.contrib.auth.views.password_reset_complete'),
                       (r'', include('registration.auth_urls')),
                       )
