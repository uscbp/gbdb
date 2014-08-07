from django.conf.urls import url, patterns
from gbdb.views.behavioral_event import CreateBehavioralEventView, UpdateBehavioralEventView, BehavioralEventDetailView, DeleteBehavioralEventView
from gbdb.views.gestural_event import GesturalEventDetailView, DeleteGesturalEventView, UpdateGesturalEventView, CreateGesturalEventView
from gbdb.views.main import IndexView
from gbdb.views.observation_session import CreateObservationSessionView, ObservationSessionDetailView, DeleteObservationSessionView, UpdateObservationSessionView, SearchObservationSessionView
from gbdb.views.primate import CreatePrimateView, PrimateDetailView, DeletePrimateView, UpdatePrimateView
from gbdb.views.gesture import CreateGestureView, GestureDetailView, DeleteGestureView, UpdateGestureView

urlpatterns = patterns('',
    url(r'^behavioral_event/(?P<pk>\d+)/$', BehavioralEventDetailView.as_view(), {}, 'behavioral_event_view'),
    url(r'^behavioral_event/(?P<pk>\d+)/delete/$', DeleteBehavioralEventView.as_view(), {}, 'behavioral_event_delete'),
    url(r'^behavioral_event/(?P<pk>\d+)/edit/$', UpdateBehavioralEventView.as_view(), {}, 'behavioral_event_edit'),
    url(r'^behavioral_event/new/$', CreateBehavioralEventView.as_view(), {}, 'behavioral_event_add'),

    url(r'^gestural_event/(?P<pk>\d+)/$', GesturalEventDetailView.as_view(), {}, 'gestural_event_view'),
    url(r'^gestural_event/(?P<pk>\d+)/delete/$', DeleteGesturalEventView.as_view(), {}, 'gestural_event_delete'),
    url(r'^gestural_event/(?P<pk>\d+)/edit/$', UpdateGesturalEventView.as_view(), {}, 'gestural_event_edit'),
    url(r'^gestural_event/new/$', CreateGesturalEventView.as_view(), {}, 'gestural_event_add'),
    
    url(r'^observation_session/(?P<pk>\d+)/$', ObservationSessionDetailView.as_view(), {}, 'observation_session_view'),
    url(r'^observation_session/(?P<pk>\d+)/delete/$', DeleteObservationSessionView.as_view(), {}, 'observation_session_delete'),
    url(r'^observation_session/(?P<pk>\d+)/edit/$', UpdateObservationSessionView.as_view(), {}, 'observation_session_edit'),
    url(r'^observation_session/new/$', CreateObservationSessionView.as_view(), {}, 'observation_session_add'),
    url(r'^observation_session/search/$', SearchObservationSessionView.as_view(), {}, 'observation_session_search'),
    
    url(r'^primate/(?P<pk>\d+)/$', PrimateDetailView.as_view(), {}, 'primate_view'),
    url(r'^primate/(?P<pk>\d+)/delete/$', DeletePrimateView.as_view(), {}, 'primate_delete'),
    url(r'^primate/(?P<pk>\d+)/edit/$', UpdatePrimateView.as_view(), {}, 'primate_edit'),
    url(r'^primate/new/$', CreatePrimateView.as_view(), {}, 'primate_add'),
    
    url(r'^gesture/(?P<pk>\d+)/$', GestureDetailView.as_view(), {}, 'gesture_view'),
    url(r'^gesture/(?P<pk>\d+)/delete/$', DeleteGestureView.as_view(), {}, 'gesture_delete'),
    url(r'^gesture/(?P<pk>\d+)/edit/$', UpdateGestureView.as_view(), {}, 'gesture_edit'),
    url(r'^gesture/new/$', CreateGestureView.as_view(), {}, 'gesture_add'),
    
    url(r'', IndexView.as_view(), {}, 'index'),
)