from rest_framework                  import permissions
from rest_framework.authtoken.models import Token
from rest_framework.exceptions       import AuthenticationFailed
from django.utils                    import timezone
from datetime                        import timedelta

class IsAuthenticated(permissions.BasePermission):
    token_inactive_message = 'Access permission error'
    token_expire_message   = 'Access permission error'
    user_inactive_message  = 'Access permission error'

    def has_permission(self, request, view):
        try:
            token = Token.objects.get(user = request.user)
        except Token.DoesNotExist:
            raise AuthenticationFailed(self.token_inactive_message)

        if not token.user.is_active:
            raise AuthenticationFailed(self.user_inactive_message)

        # This is required for the time comparison
        utc_now = timezone.now()

        if token.created < utc_now - timedelta(minutes = 3000000):  #TODO:// change expire time
            raise AuthenticationFailed(self.token_expire_message)
        
        token.created = timezone.now()
        token.save()

        return True
