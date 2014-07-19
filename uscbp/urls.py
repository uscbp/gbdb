from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from gbdb.forms import GbdbRegistrationForm
from gbdb.views.admin import GbdbRegistrationView

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gbdb.views.home', name='home'),
    # url(r'^gbdb/', include('uscbp.foo.urls')),

    (r'^gbdb/', include('gbdb.urls')),

    (r'^accounts/logout/$', 'gbdb.views.admin.logout_view', ),
    (r'^accounts/register/$', GbdbRegistrationView.as_view(form_class=GbdbRegistrationForm), {}, 'registration_register'),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^accounts/username_available/$', 'gbdb.views.admin.username_available', ),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
