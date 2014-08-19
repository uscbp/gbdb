import operator
from django.db.models import Q
from django.utils import six
from django.utils.encoding import force_text
from taggit.utils import split_strip
from gbdb.models import ObservationSession, BehavioralEvent, GesturalEvent, Primate, Gesture
from geoposition.models import compute_distance
from registration.models import User

def parse_search_string(searchstring):
    """
    Parses tag input, with multiple word input being activated and
    delineated by commas and double quotes. Quotes take precedence, so
    they may contain commas.

    Returns a sorted list of unique tag names.

    Ported from Jonathan Buchanan's `django-tagging
    <http://django-tagging.googlecode.com/>`_
    """
    if not searchstring:
        return []

    searchstring = force_text(searchstring)

    # Special case - if there are no commas or double quotes in the
    # input, we don't *do* a recall... I mean, we know we only need to
    # split on spaces.
    if ',' not in searchstring and '"' not in searchstring:
        words = list(set(split_strip(searchstring, ' ')))
        words.sort()
        return words

    words = []
    buffer = []
    # Defer splitting of non-quoted sections until we know if there are
    # any unquoted commas.
    to_be_split = []
    saw_loose_comma = False
    open_quote = False
    i = iter(searchstring)
    try:
        while True:
            c = six.next(i)
            if c == '"':
                if buffer:
                    to_be_split.append(''.join(buffer))
                    buffer = []
                    # Find the matching quote
                open_quote = True
                c = six.next(i)
                while c != '"':
                    buffer.append(c)
                    c = six.next(i)
                if buffer:
                    word = ''.join(buffer).strip()
                    if word:
                        words.append(word)
                    buffer = []
                open_quote = False
            else:
                if not saw_loose_comma and c == ',':
                    saw_loose_comma = True
                buffer.append(c)
    except StopIteration:
        # If we were parsing an open quote which was never closed treat
        # the buffer as unquoted.
        if buffer:
            if open_quote and ',' in buffer:
                saw_loose_comma = True
            to_be_split.append(''.join(buffer))
    if to_be_split:
        if saw_loose_comma:
            delimiter = ','
        else:
            delimiter = ' '
        for chunk in to_be_split:
            words.extend(split_strip(chunk, delimiter))
    words = list(set(words))
    words.sort()
    return words


def runObservationSessionSearch(search_data, userId):
    filters=[]

    op=operator.or_
    if search_data['search_options']=='all':
        op=operator.and_

    searcher=ObservationSessionSearch(search_data)

    # construct search query
    for key in search_data.iterkeys():
        # if the searcher can search by this field
        if hasattr(searcher, 'search_%s' % key):
            # add field to query
            dispatch=getattr(searcher, 'search_%s' % key)
            filters.append(dispatch(userId))

    q = reduce(op,filters)

    # get results
    if q and len(q):
        results = ObservationSession.objects.filter(q).select_related().distinct().order_by('date')
    else:
        results = ObservationSession.objects.all().select_related().order_by('date')

    filtered_results=[]
    for result in results:
        if not searcher.location:
            filtered_results.append(result)
        else:
            search_lat=searcher.location[0]
            search_long=searcher.location[1]
            search_rad=searcher.location[2]
            distance=compute_distance(float(search_lat),float(search_long),float(result.location.latitude),
                float(result.location.longitude))
            if distance<=search_rad:
                filtered_results.append(result)
    return filtered_results


class ObservationSessionSearch(object):

    def __init__(self, search_data):
        self.__dict__.update(search_data)

    def search_keywords(self, userId):
        if self.keywords:
            op=operator.or_
            if self.keywords_options=='all':
                op=operator.and_
            words=parse_search_string(self.keywords)
            notes_filters=[Q(notes__icontains=word) for word in words]
            return reduce(op,notes_filters)
        return Q()

    # search by collator
    def search_collator(self, userId):
        if self.collator:
            return Q(collator__id=userId)
        return Q()

    def search_username(self, userId):
        if self.username:
            return Q(collator__username__icontains=self.username)
        return Q()

    def search_first_name(self, userId):
        if self.first_name:
            return Q(collator__first_name__icontains=self.first_name)
        return Q()

    def search_last_name(self, userId):
        if self.last_name:
            return Q(collator__last_name__icontains=self.last_name)
        return Q()

    def search_created_from(self, userId):
        if self.created_from:
            return Q(creation_time__gte=self.created_from)
        return Q()

    def search_created_to(self, userId):
        if self.created_to:
            return Q(creation_time__lte=self.created_to)
        return Q()

    def search_date_min(self, userId):
        if self.date_min:
            return Q(date__gte=self.date_min)
        return Q()

    def search_date_max(self, userId):
        if self.date_max:
            return Q(date__lte=self.date_max)
        return Q()

    def search_location_name(self, userId):
        if self.location_name:
            op=operator.or_
            if self.location_name_options=='all':
                op=operator.and_
            words=parse_search_string(self.location_name)
            location_filters=[Q(location_name__icontains=word) for word in words]
            return reduce(op,location_filters)
        return Q()


def runBehavioralEventSearch(search_data, userId):
    filters=[]

    op=operator.or_
    if search_data['search_options']=='all':
        op=operator.and_

    searcher=BehavioralEventSearch(search_data)

    # construct search query
    for key in search_data.iterkeys():
        # if the searcher can search by this field
        if hasattr(searcher, 'search_%s' % key):
            # add field to query
            dispatch=getattr(searcher, 'search_%s' % key)
            filters.append(dispatch(userId))

    # restrict to user's own entries or those of other users that are not drafts
    if User.objects.filter(id=userId):
        user=User.objects.get(id=userId)
    else:
        user=User.get_anonymous()

    q = reduce(op,filters)

    converted_results=[]
    # get results
    if q and len(q):
        results = BehavioralEvent.objects.filter(q).select_related().distinct()
    else:
        results = BehavioralEvent.objects.all().select_related()

    for r in results:
        if r.type=='gestural':
            converted_results.append(GesturalEvent.objects.get(id=r.id))
        else:
            converted_results.append(r)

    filtered_results=[]
    for result in converted_results:
        if not searcher.location:
            filtered_results.append(result)
        else:
            search_lat=searcher.location[0]
            search_long=searcher.location[1]
            search_rad=searcher.location[2]
            distance=compute_distance(float(search_lat),float(search_long),float(result.observation_session.location.latitude),
                float(result.observation_session.location.longitude))
            if distance<=search_rad:
                filtered_results.append(result)
    return filtered_results



class BehavioralEventSearch(object):

    def __init__(self, search_data):
        self.__dict__.update(search_data)

    def search_keywords(self, userId):
        if self.keywords:
            op=operator.or_
            if self.keywords_options=='all':
                op=operator.and_
            words=parse_search_string(self.keywords)
            notes_filters=[Q(notes__icontains=word) for word in words]
            contexts_filters=[Q(contexts__names__icontains=word) for word in words]
            ethograms_filters=[Q(ethograms__names__icontains=word) for word in words]
            return reduce(op,notes_filters) | reduce(op,contexts_filters) | reduce(op,ethograms_filters)
        return Q()

    def search_type(self, userId):
        if self.type:
            return Q(type__iexact=self.type)
        return Q()

    # search by collator
    def search_collator(self, userId):
        if self.collator:
            return Q(observation_session__collator__id=userId)
        return Q()

    def search_username(self, userId):
        if self.username:
            return Q(observation_session__collator__username__icontains=self.username)
        return Q()

    def search_first_name(self, userId):
        if self.first_name:
            return Q(observation_session__collator__first_name__icontains=self.first_name)
        return Q()

    def search_last_name(self, userId):
        if self.last_name:
            return Q(observation_session__collator__last_name__icontains=self.last_name)
        return Q()

    def search_created_from(self, userId):
        if self.created_from:
            return Q(observation_session__creation_time__gte=self.created_from)
        return Q()

    def search_created_to(self, userId):
        if self.created_to:
            return Q(observation_session__creation_time__lte=self.created_to)
        return Q()

    def search_date_min(self, userId):
        if self.date_min:
            return Q(observation_session__date__gte=self.date_min)
        return Q()

    def search_date_max(self, userId):
        if self.date_max:
            return Q(observation_session__date__lte=self.date_max)
        return Q()

    def search_location_name(self, userId):
        if self.location_name:
            op=operator.or_
            if self.location_name_options=='all':
                op=operator.and_
            words=parse_search_string(self.location_name)
            location_filters=[Q(observation_session__location_name__icontains=word) for word in words]
            return reduce(op,location_filters)
        return Q()

    def search_primates_name(self, userId):
        if self.primates_name:
            return Q(primates__name__iexact=self.primates_name)
        return Q()

    def search_primates_species(self, userId):
        if self.primates_species:
            return Q(primates__species__in=self.primates_species)
        return Q()

    def search_primates_birth_date_min(self, userId):
        if self.primates_birth_date_min:
            return Q(primates__birth_date__gte=self.primates_birth_date_min)
        return Q()

    def search_primates_birth_date_max(self, userId):
        if self.primates_birth_date_max:
            return Q(primates__birth_date__lte=self.primates_birth_date_max)
        return Q()

    def search_primates_habitat(self, userId):
        if self.primates_habitat:
            return Q(primates__habitat__iexact=self.primates_habitat)
        return Q()

    def search_contexts(self, userId):
        if self.contexts:
            op=operator.or_
            if self.contexts_options=='all':
                op=operator.and_
            words=parse_search_string(self.contexts)
            context_filters=[Q(contexts__name__icontains=word) for word in words]
            return reduce(op,context_filters)
        return Q()

    def search_ethograms(self, userId):
        if self.ethograms:
            op=operator.or_
            if self.ethograms_options=='all':
                op=operator.and_
            words=parse_search_string(self.ethograms)
            ethogram_filters=[Q(ethograms__name__icontains=word) for word in words]
            return reduce(op,ethogram_filters)
        return Q()
    
    def search_gestural_signaller_name(self, userId):
        if self.type=='gestural' and self.gestural_signaller_name:
            return Q(gesturalevent__signaller__name__iexact=self.gestural_signaller_name)
        return Q()

    def search_gestural_signaller_species(self, userId):
        if self.type=='gestural' and self.gestural_signaller_species:
            return Q(gesturalevent__signaller__species__in=self.gestural_signaller_species)
        return Q()

    def search_gestural_signaller_birth_date_min(self, userId):
        if self.type=='gestural' and self.gestural_signaller_birth_date_min:
            return Q(gesturalevent__signaller__birth_date__gte=self.gestural_signaller_birth_date_min)
        return Q()

    def search_gestural_signaller_birth_date_max(self, userId):
        if self.type=='gestural' and self.gestural_signaller_birth_date_max:
            return Q(gesturalevent__signaller__birth_date__gte=self.gestural_signaller_birth_date_max)
        return Q()

    def search_gestural_signaller_habitat(self, userId):
        if self.type=='gestural' and self.gestural_signaller_habitat:
            return Q(gesturalevent__signaller__habitat__iexact=self.gestural_signaller_habitat)
        return Q()

    def search_gestural_recipient_name(self, userId):
        if self.type=='gestural' and self.gestural_recipient_name:
            return Q(gesturalevent__recipient__name__iexact=self.gestural_recipient_name)
        return Q()

    def search_gestural_recipient_species(self, userId):
        if self.type=='gestural' and self.gestural_recipient_species:
            return Q(gesturalevent__recipient__species__in=self.gestural_recipient_species)
        return Q()

    def search_gestural_recipient_birth_date_min(self, userId):
        if self.type=='gestural' and self.gestural_recipient_birth_date_min:
            return Q(gesturalevent__recipient__birth_date__gte=self.gestural_recipient_birth_date_min)
        return Q()

    def search_gestural_recipient_birth_date_max(self, userId):
        if self.type=='gestural' and self.gestural_recipient_birth_date_max:
            return Q(gesturalevent__recipient__birth_date__gte=self.gestural_recipient_birth_date_max)
        return Q()

    def search_gestural_recipient_habitat(self, userId):
        if self.type=='gestural' and self.gestural_recipient_habitat:
            return Q(gesturalevent__recipient__habitat__iexact=self.gestural_recipient_habitat)
        return Q()

    def search_gestural_gesture(self, userId):
        if self.type=='gestural' and self.gestural_gesture:
            op=operator.or_
            if self.type=='gestural' and self.gestural_gesture_options=='all':
                op=operator.and_
            words=parse_search_string(self.gestural_gesture)
            name_filters=[Q(gesturalevent__gesture__name__icontains=word) for word in words]
            description_filters=[Q(gesturalevent__gesture__description__icontains=word) for word in words]
            return reduce(op,name_filters) | reduce(op,description_filters)
        return Q()

    def search_gestural_gesture_goal(self, userId):
        if self.type=='gestural' and self.gestural_gesture_goal:
            op=operator.or_
            if self.type=='gestural' and self.gestural_gesture_goal_options=='all':
                op=operator.and_
            words=parse_search_string(self.gestural_gesture_goal)
            goal_filters=[Q(gesturalevent__gesture__goal__icontains=word) for word in words]
            return reduce(op,goal_filters)
        return Q()

    def search_gestural_gesture_signaller_body_parts(self, userId):
        if self.type=='gestural' and self.gestural_gesture_signaller_body_parts:
            op=operator.or_
            if self.type=='gestural' and self.gestural_gesture_signaller_body_parts_options=='all':
                op=operator.and_
            words=parse_search_string(self.gestural_gesture_signaller_body_parts)
            signaller_body_parts_filters=[Q(gesturalevent__gesture__signaller_body_parts__name__icontains=word) for word in words]
            return reduce(op,signaller_body_parts_filters)
        return Q()

    def search_gestural_gesture_recipient_body_parts(self, userId):
        if self.type=='gestural' and self.gestural_gesture_recipient_body_parts:
            op=operator.or_
            if self.type=='gestural' and self.gestural_gesture_recipient_body_parts_options=='all':
                op=operator.and_
            words=parse_search_string(self.gestural_gesture_recipient_body_parts)
            recipient_body_parts_filters=[Q(gesturalevent__gesture__recipient_body_parts__name__icontains=word) for word in words]
            return reduce(op,recipient_body_parts_filters)
        return Q()

    def search_gestural_gesture_audible(self, userId):
        if self.type=='gestural' and self.gestural_gesture_audible:
            return Q(gesturalevent__gesture__audible__iexact=self.gestural_gesture_audible)
        return Q()

    def search_gestural_recipient_response(self, userId):
        if self.type=='gestural' and self.gestural_recipient_response:
            op=operator.or_
            if self.type=='gestural' and self.gestural_recipient_response_options=='all':
                op=operator.and_
            words=parse_search_string(self.gestural_recipient_response)
            recipient_response_filters=[Q(gesturalevent__recipient_response__icontains=word) for word in words]
            return reduce(op,recipient_response_filters)
        return Q()

    def search_gestural_goal_met(self, userId):
        if self.type=='gestural' and self.gestural_goal_met:
            return Q(gesturalevent__goal_met__iexact=self.gestural_goal_met)
        return Q()


def runPrimateSearch(search_data, userId):
    filters=[]

    op=operator.or_
    if search_data['search_options']=='all':
        op=operator.and_

    searcher=PrimateSearch(search_data)

    # construct search query
    for key in search_data.iterkeys():
        # if the searcher can search by this field
        if hasattr(searcher, 'search_%s' % key):
            # add field to query
            dispatch=getattr(searcher, 'search_%s' % key)
            filters.append(dispatch(userId))

    q = reduce(op,filters)

    # get results
    if q and len(q):
        results = Primate.objects.filter(q).select_related().distinct().order_by('name')
    else:
        results = Primate.objects.all().select_related().order_by('name')

    filtered_results=[]
    for result in results:
        if not searcher.location:
            filtered_results.append(result)
        else:
            search_lat=searcher.location[0]
            search_long=searcher.location[1]
            search_rad=searcher.location[2]
            distance=compute_distance(float(search_lat),float(search_long),float(result.location.latitude),
                float(result.location.longitude))
            if distance<=search_rad:
                filtered_results.append(result)
    return filtered_results


class PrimateSearch(object):

    def __init__(self, search_data):
        self.__dict__.update(search_data)

    def search_name(self, userId):
        if self.name:
            return Q(name__iexact=self.name)
        return Q()

    def search_species(self, userId):
        if self.species:
            return Q(species__in=self.species)
        return Q()

    def search_birth_date_min(self, userId):
        if self.birth_date_min:
            return Q(birth_date__gte=self.birth_date_min)
        return Q()

    def search_birth_date_max(self, userId):
        if self.birth_date_max:
            return Q(birth_date__lte=self.birth_date_max)
        return Q()

    def search_location_name(self, userId):
        if self.location_name:
            op=operator.or_
            if self.location_name_options=='all':
                op=operator.and_
            words=parse_search_string(self.location_name)
            location_filters=[Q(location_name__icontains=word) for word in words]
            return reduce(op,location_filters)
        return Q()

    def search_habitat(self, userId):
        if self.habitat:
            return Q(habitat__iexact=self.habitat)
        return Q()


def runGestureSearch(search_data, userId):
    filters=[]

    op=operator.or_
    if search_data['search_options']=='all':
        op=operator.and_

    searcher=GestureSearch(search_data)

    # construct search query
    for key in search_data.iterkeys():
        # if the searcher can search by this field
        if hasattr(searcher, 'search_%s' % key):
            # add field to query
            dispatch=getattr(searcher, 'search_%s' % key)
            filters.append(dispatch(userId))

    q = reduce(op,filters)

    # get results
    if q and len(q):
        results = Gesture.objects.filter(q).select_related().distinct()
    else:
        results = Gesture.objects.all().select_related()

    return results.order_by('name')


class GestureSearch(object):

    def __init__(self, search_data):
        self.__dict__.update(search_data)

    def search_keywords(self, userId):
        if self.keywords:
            op=operator.or_
            if self.keywords_options=='all':
                op=operator.and_
            words=parse_search_string(self.keywords)
            name_filters=[Q(name__icontains=word) for word in words]
            description_filters=[Q(description__icontains=word) for word in words]
            return reduce(op,name_filters) | reduce(op,description_filters)
        return Q()
    
    def search_name(self, userId):
        if self.name:
            op=operator.or_
            if self.name_options=='all':
                op=operator.and_
            words=parse_search_string(self.name)
            name_filters=[Q(name__icontains=word) for word in words]
            return reduce(op,name_filters)
        return Q()

    def search_description(self, userId):
        if self.description:
            op=operator.or_
            if self.description_options=='all':
                op=operator.and_
            words=parse_search_string(self.description)
            description_filters=[Q(description__icontains=word) for word in words]
            return reduce(op,description_filters)
        return Q()

    def search_goal(self, userId):
        if self.goal:
            op=operator.or_
            if self.goal_options=='all':
                op=operator.and_
            words=parse_search_string(self.goal)
            goal_filters=[Q(goal__icontains=word) for word in words]
            return reduce(op,goal_filters)
        return Q()

    def search_signaller_body_parts(self, userId):
        if self.signaller_body_parts:
            return Q(signaller_body_parts__in=self.signaller_body_parts)
        return Q()

    def search_recipient_body_parts(self, userId):
        if self.recipient_body_parts:
            return Q(recipient_body_parts__in=self.recipient_body_parts)
        return Q()

    def search_audible(self, userId):
        if self.audible:
            return Q(audible__iexact=self.audible)
        return Q()