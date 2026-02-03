import traceback
from rest_framework import status
from rest_framework.response import Response
from GSE_Backend.errors.ErrorDictionary import CustomError
from ..UserManager.UserHelper import UserHelper
from api.Models.user_table_layout import UserTableLayoutModel

class UserTableLayoutHelper():
  
    @staticmethod
    def create_or_update_by_key(user,key,value):
        object,response=UserTableLayoutHelper.get_by_key(user,key)
        
        if response.status_code==status.HTTP_404_NOT_FOUND:
            object,response=UserTableLayoutHelper.create_null_by_key(user,key)
    
        if not object:
            return response
    
        object.value=value
        object.save(using=user.db_access)
        
        return Response(status=status.HTTP_200_OK)
    
    @staticmethod
    def get_by_key(user,key):
        detailed=UserHelper.get_detailed_user_obj(user.email,user.db_access)
    
        try:
            return UserTableLayoutModel.objects.using(user.db_access).get(user=detailed,key=key),Response(status=status.HTTP_302_FOUND)
        except UserTableLayoutModel.DoesNotExist as error:
            return None,Response(status=status.HTTP_404_NOT_FOUND)
        except:
            traceback.print_exc()
            return None,Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_null_by_key(user,key):
        detailed=UserHelper.get_detailed_user_obj(user.email,user.db_access)

        try:
            object=UserTableLayoutModel(
                user=detailed,
                key=key
            )
            
            object.save(using=user.db_access)
            
            return object,Response(status=status.HTTP_200_OK)
        except:
            traceback.print_exc()
            return None,Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def get_all(user):
        detailed=UserHelper.get_detailed_user_obj(user.email,user.db_access)
    
        try:
            return UserTableLayoutModel.objects.using(user.db_access).filter(user=detailed),Response(status=status.HTTP_302_FOUND)
        except UserTableLayoutModel.DoesNotExist as error:
            return None,Response(status=status.HTTP_404_NOT_FOUND)
        except:
            traceback.print_exc()
            return None,Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_all_dict(user):
        objects,response=UserTableLayoutHelper.get_all(user)

        if response.status_code!=status.HTTP_302_FOUND:
            return None,response

        dict={}
        for object in objects:
            dict[object.key]=object.value

        return dict,Response(status=status.HTTP_302_FOUND)