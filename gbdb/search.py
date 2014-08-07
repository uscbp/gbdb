import operator
from django.db.models import Q
from django.utils import six
from django.utils.encoding import force_text
from tagging.utils import split_strip
from gbdb.models import ObservationSession
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

def runObservationSessionSearch(search_data, userId, exclude=None):
    filters=[]

    op=operator.or_
    if search_data['search_options']=='all':
        op=operator.and_

    # create Model search
    searcher=ObservationSessionSearch(search_data)

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

    # get results
    if q and len(q):
        print(q)
        results = ObservationSession.objects.filter(q).select_related().distinct()
    else:
        results = ObservationSession.objects.all().select_related()

    return results.order_by('date')


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

    def search_location(self, userId):
        if self.location:
            op=operator.or_
            if self.location_options=='all':
                op=operator.and_
            words=parse_search_string(self.location)
            location_filters=[Q(location__icontains=word) for word in words]
            return reduce(op,location_filters)
        return Q()
