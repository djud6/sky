import json
from core.PusherManager.PusherHelper import PusherHelper
import logging
from rest_framework.response import Response
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework import status

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class PusherHandler:

    @staticmethod
    def handle_authentication(request_data):
        try:
            channel = "channel_name"
            socket_id = "socket_id"
            if request_data is None or channel not in request_data or socket_id not in request_data:
                return Response(CustomError.get_full_error_json(CustomError.PSHRFNP_0), status=status.HTTP_400_BAD_REQUEST)
            auth = PusherHelper.authenticate(request_data.get(channel), request_data.get(socket_id))
            return Response(auth, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.PSHR_0, e))
            return Response(CustomError.get_full_error_json(CustomError.PSHR_0, e), status=status.HTTP_400_BAD_REQUEST)

