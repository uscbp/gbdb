from django.conf.urls import url, patterns
from gbdb.views.main import IndexView

urlpatterns = patterns('',

    url(r'', IndexView.as_view(), {}, 'index'),
)