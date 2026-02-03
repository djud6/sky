from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.AssetManager.AssetHelper import AssetHelper
from core.DisposalManager.DisposalHandler import DisposalHandler
from core.UserManager.UserHelper import UserHelper
from api.Models.dailyinspectionmodel import DailyInspection
from api.Serializers.serializers import DailyInspectionModelSerializer
import logging
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from GSE_Backend.errors.ErrorDictionary import CustomError
from rest_framework.response import Response
from rest_framework import status
from core.Helper import HelperMethods
from django.db.models import Q


class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)
    
# this view returns all daily inspection
class GetAllDailyInspection(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
                detailed_user_info= UserHelper.get_detailed_user_obj(request.user.email, request.user.db_access)

                if not detailed_user_info == status.HTTP_404_NOT_FOUND:
                     daily_inspections = DailyInspection.objects.using(request.user.db_access).all()
                     daily_inspection_serializer = DailyInspectionModelSerializer(daily_inspections, many=True)
                return Response(daily_inspection_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
            

# this view returns daily inspection by VIN
class GetDailyInspectionsByVIN(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, _vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)
        try:
                detailed_user_info= UserHelper.get_detailed_user_obj(request.user.email, request.user.db_access)

                if not detailed_user_info == status.HTTP_404_NOT_FOUND:
                     daily_inspections_by_vin = DailyInspection.objects.using(request.user.db_access).filter(Q(VIN = _vin)).order_by('id').all()
                     daily_inspection_by_vin_serializer = DailyInspectionModelSerializer(daily_inspections_by_vin, many=True)
                return Response(daily_inspection_by_vin_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
        

# this view Adds / edits the daily inspection by VIN:
class AddDailyInspectionByVIN(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,) 

    def post (self, request, _vin):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)

        if not AssetHelper.check_asset_status_active(_vin, request.user.db_access, allow_inoperative=False):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                               CustomError.get_error_user(CustomError.TUF_16)))
            return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                            CustomError.get_error_user(CustomError.TUF_16)),
                            status=status.HTTP_400_BAD_REQUEST)

        data = {
                'VIN' : _vin,
                'inspection_date': request.data.get('inspection_date'),
                'pfd_lifejacket_ledger': request.data.get('pfd_lifejacket_ledger'),
                'throw_bags': request.data.get('throw_bags'),
                'heaving_line': request.data.get('heaving_line'),
                'liferings': request.data.get('liferings'),
                'reboarding_device': request.data.get('reboarding_device'),
                'watertight_flashlight': request.data.get('watertight_flashlight'),
                'pyrotechnic_flares': request.data.get('pyrotechnic_flares'),
                'first_aid_kit': request.data.get('first_aid_kit'),
                'engine_working': request.data.get('engine_working'),
                'marine_vhf_radio': request.data.get('marine_vhf_radio'),
                'police_radio': request.data.get('police_radio'),
                'epirb_registered': request.data.get('epirb_registered'),
                'bilge_pump_clear': request.data.get('bilge_pump_clear'),
                'steering_controls_operable': request.data.get('steering_controls_operable'),
                'hatches_operable': request.data.get('hatches_operable'),
                'training_skills_exercised': request.data.get('training_skills_exercised'),
                'drills_entered_logbook': request.data.get('drills_entered_logbook'),
                'emergency_briefings_conducted': request.data.get('emergency_briefings_conducted'),
                'fire_extinguishers_inspected': request.data.get('fire_extinguishers_inspected'),
                'regular_inspections_completed': request.data.get('regular_inspections_completed'),
                'electrical_inspections_completed': request.data.get('electrical_inspections_completed'),
                'broken_cracked_lenses': request.data.get('broken_cracked_lenses'),
                'pfd_lifejacket_ledger': request.data.get('pfd_lifejacket_ledger'),
                'lights_functioning': request.data.get('lights_functioning'),
                'fuel_connections_good': request.data.get('fuel_connections_good'),
                'fuel_containers_stored_properly': request.data.get('fuel_containers_stored_properly'),
                'ground_tackle_inspected': request.data.get('ground_tackle_inspected'),
                'bitter_end_attached': request.data.get('bitter_end_attached'),
                'anchor_secured': request.data.get('anchor_secured'),
                'welds_bolts_screws_good': request.data.get('welds_bolts_screws_good'),
                'grab_lines_good': request.data.get('grab_lines_good'),
                'operators_trained': request.data.get('operators_trained'),
                'vessel_damaged_since_last_report': request.data.get('vessel_damaged_since_last_report'),
                'structural_changes_made_since_last_report': request.data.get('structural_changes_made_since_last_report')
            } 

        try:

            if DailyInspection.objects.filter(VIN=_vin).exists():
                instance = DailyInspection.objects.get(VIN=_vin)
                serializer = DailyInspectionModelSerializer(instance, data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = DailyInspectionModelSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)