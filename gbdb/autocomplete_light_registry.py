import autocomplete_light
from gbdb.models import Context, Ethogram
from registration.models import User

autocomplete_light.register(Context,
    search_fields=['^name'],
    autocomplete_js_attributes={'placeholder': 'add another context',},
)

autocomplete_light.register(Ethogram,
    search_fields=['^name'],
    autocomplete_js_attributes={'placeholder': 'add another ethogram',},
)

autocomplete_light.register(User,
    search_fields=['^first_name', '^last_name', '^username'],
    autocomplete_js_attributes={'placeholder': 'add another user',},
)
