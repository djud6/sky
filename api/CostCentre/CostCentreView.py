from rest_framework.views import APIView
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from core.CostCentreManager.CostCentreHandler import CostCentreHandler

class GetAll(APIView):

    def get(self,request):
        if auth_token_check(request.user):
            return Response(CustomError.get_full_error_json(CustomError.IT_0),status=status.HTTP_400_BAD_REQUEST)

        return CostCentreHandler.handle_get_all(request.user)