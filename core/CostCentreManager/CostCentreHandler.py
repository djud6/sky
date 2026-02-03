from rest_framework.response import Response
from rest_framework import status
from .CostCentreHelper import CostCentreHelper
from api.Serializers.serializers import CostCentreSerializer
from GSE_Backend.errors.ErrorDictionary import CustomError

class CostCentreHandler():

    @staticmethod
    def handle_get_all(user):
        try:
            qs=CostCentreHelper.get_all(user.db_access)
            serializer=CostCentreSerializer(qs,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response(CustomError.get_full_error_json(CustomError.G_0,e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)