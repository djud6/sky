from rest_framework.views import APIView
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from core.UserTableLayoutManager.UserTableLayoutHandler import UserTableLayoutHandler

class SetByKey(APIView):
    def post(self,request):
        if auth_token_check(request.user):
            return Response(CustomError.get_full_error_json(CustomError.IT_0),status=status.HTTP_400_BAD_REQUEST)

        return UserTableLayoutHandler.handle_set_by_key(request.user,request.data)

class GetByKey(APIView):
    def post(self,request):
        if auth_token_check(request.user):
            return Response(CustomError.get_full_error_json(CustomError.IT_0),status=status.HTTP_400_BAD_REQUEST)

        return UserTableLayoutHandler.handle_get_by_key(request.user,request.data)

class GetAll(APIView):
    def get(self,request):
        if auth_token_check(request.user):
            return Response(CustomError.get_full_error_json(CustomError.IT_0),status=status.HTTP_400_BAD_REQUEST)

        return UserTableLayoutHandler.handle_get_all_dict(request.user)

class DeleteByKey(APIView):
    def post(self,request):
        if auth_token_check(request.user):
            return Response(CustomError.get_full_error_json(CustomError.IT_0),status=status.HTTP_400_BAD_REQUEST)

        return UserTableLayoutHandler.handle_delete_by_key(request.user,request.data)