from api.Models.cost_centre import CostCentreModel
from rest_framework import status
from rest_framework.response import Response
from GSE_Backend.errors.ErrorDictionary import CustomError

class CostCentreHelper():

    @staticmethod
    def get_all(db_name):
        return CostCentreModel.objects.using(db_name).all()

    @staticmethod
    def get_by_name(db_name,target_name):
        try:
            return CostCentreModel.objects.using(db_name).get(name=target_name),Response(status=status.HTTP_302_FOUND)
        except:
            return None,Response(CustomError.get_full_error_json(CustomError.G_0),status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_by_id(db_name,target_id):
        try:
            return CostCentreModel.objects.using(db_name).get(cost_centre_id=target_id),Response(status=status.HTTP_302_FOUND)
        except:
            return None,Response(CustomError.get_full_error_json(CustomError.G_0),status=status.HTTP_400_BAD_REQUEST)