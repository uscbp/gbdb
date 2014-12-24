from django.conf.urls import *
from gbdb.views.behavioral_event import CreateBehavioralEventView, UpdateBehavioralEventView, DeleteBehavioralEventView, SearchBehavioralEventView
from gbdb.views.location import SavedLocationDetailView, CreateSavedLocationView
from gbdb.views.main import IndexView
from gbdb.views.observation_session import CreateObservationSessionView, ObservationSessionDetailView, DeleteObservationSessionView, UpdateObservationSessionView, SearchObservationSessionView, ManageObservationSessionPermissionsView
from gbdb.views.primate import CreatePrimateView, PrimateDetailView, DeletePrimateView, UpdatePrimateView, SearchPrimateView
from gbdb.views.gesture import CreateGestureView, GestureDetailView, DeleteGestureView, UpdateGestureView, SearchGestureView
from gbdb.views.admin import AdminDetailView, CreateGroupView, UpdateGroupView, DeleteGroupView, GroupDetailView

import autocomplete_light
autocomplete_light.autodiscover()

urlpatterns = patterns('',
                       
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url(r'^timeline/', include('timelinejs.urls')),
                       
    url(r'^behavioral_event/(?P<pk>\d+)/delete/$', DeleteBehavioralEventView.as_view(), {}, 'behavioral_event_delete'),
    url(r'^behavioral_event/(?P<pk>\d+)/edit/$', UpdateBehavioralEventView.as_view(), {}, 'behavioral_event_edit'),
    url(r'^behavioral_event/new/$', CreateBehavioralEventView.as_view(), {}, 'behavioral_event_add'),
    url(r'^behavioral_event/search/$', SearchBehavioralEventView.as_view(), {}, 'behavioral_event_search'),

    url(r'^observation_session/(?P<pk>\d+)/$', ObservationSessionDetailView.as_view(), {}, 'observation_session_view'),
    url(r'^observation_session/(?P<pk>\d+)/delete/$', DeleteObservationSessionView.as_view(), {}, 'observation_session_delete'),
    url(r'^observation_session/(?P<pk>\d+)/edit/$', UpdateObservationSessionView.as_view(), {}, 'observation_session_edit'),
    url(r'^observation_session/new/$', CreateObservationSessionView.as_view(), {}, 'observation_session_add'),
    url(r'^observation_session/search/$', SearchObservationSessionView.as_view(), {}, 'observation_session_search'),
    url(r'^observation_session/(?P<pk>\d+)/permissions/$', ManageObservationSessionPermissionsView.as_view(), {}, 'manage_permissions'),
    
    url(r'^primate/(?P<pk>\d+)/$', PrimateDetailView.as_view(), {}, 'primate_view'),
    url(r'^primate/(?P<pk>\d+)/delete/$', DeletePrimateView.as_view(), {}, 'primate_delete'),
    url(r'^primate/(?P<pk>\d+)/edit/$', UpdatePrimateView.as_view(), {}, 'primate_edit'),
    url(r'^primate/new/$', CreatePrimateView.as_view(), {}, 'primate_add'),
    url(r'^primate/search/$', SearchPrimateView.as_view(), {}, 'primate_search'),
    
    url(r'^gesture/(?P<pk>\d+)/$', GestureDetailView.as_view(), {}, 'gesture_view'),
    url(r'^gesture/(?P<pk>\d+)/delete/$', DeleteGestureView.as_view(), {}, 'gesture_delete'),
    url(r'^gesture/(?P<pk>\d+)/edit/$', UpdateGestureView.as_view(), {}, 'gesture_edit'),
    url(r'^gesture/new/$', CreateGestureView.as_view(), {}, 'gesture_add'),
    url(r'^gesture/search/$', SearchGestureView.as_view(), {}, 'gesture_search'),

    url(r'^saved_location/$', SavedLocationDetailView.as_view(), {}, 'saved_location_view'),
    url(r'^saved_location/new/$', CreateSavedLocationView.as_view(), {}, 'saved_location_add'),
     
    url(r'^admin/$', AdminDetailView.as_view(), {}, 'admin'),
    url(r'^group/new/$', CreateGroupView.as_view(), {}, 'group_add'),
    url(r'^group/(?P<pk>\d+)/edit/$', UpdateGroupView.as_view(), {}, 'group_edit'),
    url(r'^group/(?P<pk>\d+)/delete/$', DeleteGroupView.as_view(), {}, 'group_delete'),
    url(r'^group/(?P<pk>\d+)/$', GroupDetailView.as_view(), {}, 'group_view'),

    url(r'', IndexView.as_view(), {}, 'index'),
)