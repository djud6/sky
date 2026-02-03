import traceback
from rest_framework.response import Response
from rest_framework import status
from GSE_Backend.errors.ErrorDictionary import CustomError
from .UserTableLayoutHelper import UserTableLayoutHelper
from api.Serializers.serializers import UserTableLayoutSerializer

class UserTableLayoutHandler():

    @staticmethod
    def handle_set_by_key(user,data):
        try:
            key=data.get("key")
            value=data.get("value")
            if not key or not value:
                return Response(CustomError.I_0,status.HTTP_400_BAD_REQUEST)
            
            return UserTableLayoutHelper.create_or_update_by_key(user,key,value)
        except Exception as e:
            traceback.print_exc()
            return Response(CustomError.get_full_error_json(CustomError.G_0,e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_get_by_key(user,data):
        try:
            key=data.get("key")
            if not key:
                return Response(CustomError.I_0,status.HTTP_400_BAD_REQUEST)
            
            object,response=UserTableLayoutHelper.get_by_key(user,key)
    
            if response.status_code==status.HTTP_302_FOUND:
                serializer=UserTableLayoutSerializer(object)
                return Response(serializer.data,status=status.HTTP_200_OK)
    
            return response
        except Exception as e:
            traceback.print_exc()
            return Response(CustomError.get_full_error_json(CustomError.G_0,e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_get_all(user):
        try:
            objects,response=UserTableLayoutHelper.get_all(user)
    
            if response.status_code==status.HTTP_302_FOUND:
                serializer=UserTableLayoutSerializer(objects,many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)
    
            return response
        except Exception as e:
            traceback.print_exc()
            return Response(CustomError.get_full_error_json(CustomError.G_0,e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_get_all_dict(user):
        try:
            dict,response=UserTableLayoutHelper.get_all_dict(user)
    
            if response.status_code==status.HTTP_302_FOUND:
                return Response(dict,status=status.HTTP_200_OK)
    
            return response
        except Exception as e:
            traceback.print_exc()
            return Response(CustomError.get_full_error_json(CustomError.G_0,e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_delete_by_key(user,data):
        try:
            key=data.get("key")
            if not key:
                return Response(CustomError.I_0,status.HTTP_400_BAD_REQUEST)
            
            object,response=UserTableLayoutHelper.get_by_key(user,key)
    
            if response.status_code==status.HTTP_302_FOUND:
                object.delete()
                return Response(status=status.HTTP_200_OK)
    
            return response
        except Exception as e:
            traceback.print_exc()
            return Response(CustomError.get_full_error_json(CustomError.G_0,e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)