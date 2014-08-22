from ajax_select import LookupChannel
from gbdb.models import Context

class ContextLookup(LookupChannel):

    model = Context

    def get_query(self,q,request):
        return Context.objects.filter(name__icontains=q).order_by('name')
    
    def format_result(self, obj):
        return obj.name

    def format_item(self, obj):
        return obj.name

    def get_objects(self,ids):
        return Context.objects.filter(pk__in=ids).order_by('name')
    