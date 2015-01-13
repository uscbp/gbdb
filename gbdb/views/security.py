from guardian.mixins import PermissionRequiredMixin
from gbdb.models import ObservationSession

class PermissionRequiredPublicMixin(PermissionRequiredMixin):

    def check_permissions(self, request):

        obj = (hasattr(self, 'get_object') and self.get_object()
               or getattr(self, 'object', None))

        perms=self.get_required_permissions(request)
        view_only=True
        for perm in perms:
            (app,label)=perm.split('.')
            if not label.startswith('view'):
                view_only=False
                break
        if not view_only or not obj.public:
            return super(PermissionRequiredPublicMixin,self).check_permissions(request)
        

class BehavioralEventPermissionRequiredMixin(PermissionRequiredMixin):

    def check_permissions(self, request):
        
        obs_id = self.request.GET.get('observation_session')
        obs = None
        
        print obs_id

        if obs_id == None:
            be = (hasattr(self, 'get_object') and self.get_object() or getattr(self, 'object', None))
            obs = be.observation_session
        else:
            obs = ObservationSession.objects.get(id=self.request.GET.get('observation_session'))

        edit =  self.request.user.has_perm('gbdb.change_observationsession', obs)

        return not edit

        
        