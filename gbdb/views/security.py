from guardian.mixins import PermissionRequiredMixin

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