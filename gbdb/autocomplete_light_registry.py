import autocomplete_light
from gbdb.models import Context, Ethogram

autocomplete_light.register(Context,
    search_fields=['^name'],
    autocomplete_js_attributes={'placeholder': 'add another context',},
)

autocomplete_light.register(Ethogram,
    search_fields=['^name'],
    autocomplete_js_attributes={'placeholder': 'add another ethogram',},
)
