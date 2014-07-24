from django.conf.urls import url, patterns
from gbdb.views.main import IndexView
from gbdb.views.observation_session import CreateObservationSessionView, ObservationSessionDetailView, DeleteObservationSessionView, UpdateObservationSessionView
from gbdb.views.primate import CreatePrimateView, PrimateDetailView, DeletePrimateView, UpdatePrimateView

urlpatterns = patterns('',
    url(r'^observation_session/(?P<pk>\d+)/$', ObservationSessionDetailView.as_view(), {}, 'observation_session_view'),
    url(r'^observation_session/(?P<pk>\d+)/delete/$', DeleteObservationSessionView.as_view(), {}, 'observation_session_delete'),
    url(r'^observation_session/(?P<pk>\d+)/edit/$', UpdateObservationSessionView.as_view(), {}, 'observation_session_edit'),
    url(r'^observation_session/new/$', CreateObservationSessionView.as_view(), {}, 'observation_session_add'),
    
    url(r'^primate/(?P<pk>\d+)/$', PrimateDetailView.as_view(), {}, 'primate_view'),
    url(r'^primate/(?P<pk>\d+)/delete/$', DeletePrimateView.as_view(), {}, 'primate_delete'),
    url(r'^primate/(?P<pk>\d+)/edit/$', UpdatePrimateView.as_view(), {}, 'priamte_edit'),
    url(r'^primate/new/$', CreatePrimateView.as_view(), {}, 'primate_add'),
    
    url(r'', IndexView.as_view(), {}, 'index'),
)