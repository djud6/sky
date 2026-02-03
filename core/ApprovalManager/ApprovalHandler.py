from core.PusherManager.PusherHelper import PusherHelper
from rest_framework.response import Response
from rest_framework import status
from api.Models.approval import Approval
from GSE_Backend.errors.ErrorDictionary import CustomError
from .ApprovalHelper import ApprovalHelper
from .ApprovalUpdater import ApprovalUpdater
from ..AssetManager.AssetHelper import AssetHelper
from ..UserManager.UserHelper import UserHelper
from ..HistoryManager.ApprovalHistory import ApprovalHistory
from api.Serializers.serializers import ApprovalSerializer, LinkedApprovalSerializer
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class ApprovalHandler():

    # ----------------------------------------------------------------------------------

    @staticmethod
    def handle_create_approval_request(request_data, user):

        try:

            if not AssetHelper.check_asset_status_active(request_data.get("VIN"), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            # Create approval entry
            approval_obj, approval_entry_response = ApprovalUpdater.create_approval(request_data, user)
            if approval_entry_response.status_code != status.HTTP_201_CREATED:
                return approval_entry_response

            # Set one of the FK request fields
            updated_approval_obj, approval_update_response = ApprovalUpdater.set_fk_field(approval_obj, request_data, user.db_access)
            if approval_update_response.status_code != status.HTTP_202_ACCEPTED:
                ApprovalUpdater.delete_approval_entry(approval_obj)
                return approval_update_response

            # Create approval history record
            db_name = user.db_access
            detailed_user = UserHelper.get_detailed_user_obj(user.email, db_name)
            company_name = detailed_user.company.company_name
            channel_name = company_name
            pusher_payload = {'location': approval_obj.location.location_id}
            history_func = ApprovalHistory.create_approval_record_from_obj
            pusher_helper = PusherHelper(channel_name, PusherHelper.ApprovalCreatedEvent, pusher_payload, False, history_func)
            if(not pusher_helper.push(updated_approval_obj)):
                Logger.getLogger().error(CustomError.MHF_8)
                return Response(CustomError.get_full_error_json(CustomError.MHF_8), status=status.HTTP_400_BAD_REQUEST)

            return Response({"approval_id": updated_approval_obj.approval_id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------

    @staticmethod
    def handle_set_approval_result(request):
        try:
            approval_obj, approval_response = ApprovalHelper.get_approval_by_id(request.data.get("approval_id"), request.user.db_access)
            if approval_response.status_code != status.HTTP_302_FOUND:
                return approval_response

            if not AssetHelper.check_asset_status_active(approval_obj.VIN, request.user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)
            
            detailed_user = UserHelper.get_detailed_user_obj(request.user.email, request.user.db_access)
            valid_manager_emails = UserHelper.get_managers_emails_by_location(request.user.db_access, [approval_obj.location])

            # check if current user can approve
            if not ApprovalHelper.user_can_approve(detailed_user, approval_obj, valid_manager_emails):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.ASUF_0))
                return Response(CustomError.get_full_error_json(CustomError.ASUF_0), status=status.HTTP_400_BAD_REQUEST)

            # set is_approved to _status
            approval_obj, approval_update_response = ApprovalUpdater.set_approval_status(approval_obj, request.data, detailed_user, request.user.db_access)
            if approval_update_response.status_code != status.HTTP_202_ACCEPTED:
                return approval_update_response
            if (approval_obj.is_approved):
                event_name = PusherHelper.ApprovalApprovedEvent
            else:
                event_name = PusherHelper.ApprovalDeniedEvent
                
            # Create approval history record
            db_name = request.user.db_access
            detailed_user = UserHelper.get_detailed_user_obj(request.user.email, db_name)
            company_name = detailed_user.company.company_name
            channel_name = company_name
            pusher_payload = {'location': approval_obj.location.location_id}
            history_func = ApprovalHistory.create_approval_record_from_obj
            pusher_helper = PusherHelper(channel_name, event_name, pusher_payload, False, history_func)
            if(not pusher_helper.push(approval_obj)):
                Logger.getLogger().error(CustomError.MHF_8)
                return Response(CustomError.get_full_error_json(CustomError.MHF_8), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------

    @staticmethod
    def handle_get_requested_approvals(request):
        try:
            detailed_user_id = UserHelper.get_detailed_user_obj(request.user.email, request.user.db_access).detailed_user_id
            approval_qs = ApprovalHelper.select_related_to_approval(Approval.objects.using(request.user.db_access).filter(requesting_user=detailed_user_id))
            ser_approvals = LinkedApprovalSerializer(approval_qs, many=True)
            return Response(ser_approvals.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------

    @staticmethod
    def handle_get_approve_approvals(request):
        try:
            user_locations = UserHelper.get_user_locations_by_email(request.user.email, request.user.db_access)
            approval_qs = ApprovalHelper.select_related_to_approval(ApprovalHelper.get_approvals_by_locations(user_locations, request.user.db_access).exclude(requesting_user__email=request.user.email))
            ser_approvals = LinkedApprovalSerializer(approval_qs, many=True)
            return Response(ser_approvals.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------
