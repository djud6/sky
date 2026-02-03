from django.conf import settings
from core.Helper import HelperMethods

class AuthHelper:

    @staticmethod
    def authenticate_ghg_request(request):
        api_key = HelperMethods.json_str_to_dict(settings.INTERNAL_INTEGRATION_SYSTEM_HEADERS).get("Authorization")
        if not api_key == request.META.get('HTTP_AUTHORIZATION', None):
            return False
        return True
