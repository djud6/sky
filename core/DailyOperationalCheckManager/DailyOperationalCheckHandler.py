from core.PusherManager.PusherHelper import PusherHelper
from core.Helper import HelperMethods
from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_model import AssetModel
from api.Models.asset_daily_checks import AssetDailyChecksModel
from .DailyOperationalCheckHelper import DailyOperationalCheckHelper
from .DailyOperationalCheckUpdater import DailyOperationalCheckUpdater
from ..AssetManager.AssetUpdater import AssetUpdater, AssetHelper
from ..NotificationManager.NotificationHelper import NotificationHelper
from api.Serializers.serializers import AssetModelSerializer, LightAssetDailyChecksSerializer, AssetDailyChecksSerializer, LightAssetModelSerializer
from ..HistoryManager.AssetHistory import AssetHistory
from ..UserManager.UserHelper import UserHelper
from ..HistoryManager.OperatorCheckHistory import OperatorCheckHistory
from ..FileManager.PdfManager import PdfManager
from ..UserManager.UserHelper import UserHelper
from communication.EmailService.EmailService import Email
from GSE_Backend.errors.ErrorDictionary import CustomError
from ..FileManager.PdfManager import PdfManager
from communication.EmailService.EmailService import Email
import logging
from ..EngineManager.EngineHandler import EngineHandler

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class DailyOperationalCheckHandler():

    @staticmethod
    def handle_add_daily_operational_check_by_VIN(request):
        try:
          
            if not AssetHelper.check_asset_status_active(request.data.get("data").get("VIN"),
                                                         request.user.db_access, allow_inoperative=False):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            daily_check_data = DailyOperationalCheckHelper.update_daily_op_check_dict(request.data.get("data"), request.user.db_access)
            comments = request.data.get("comments")

            # Check to see if the request has the fields required by the asset
            check_status = DailyOperationalCheckHelper.check_request_info_present(daily_check_data, request.user.db_access)
            if check_status.status_code != status.HTTP_200_OK:
                return check_status

            serializer = AssetDailyChecksSerializer(data=daily_check_data)
            if(serializer.is_valid()):
            
                # Check if comments are valid
                check_comments_response = DailyOperationalCheckHelper.check_if_check_is_valid(comments)
                if check_comments_response.status_code != status.HTTP_200_OK:
                    return check_comments_response

                op_check_obj = serializer.save()

                # Add comments
                add_comments_response = DailyOperationalCheckUpdater.add_daily_check_comments(comments, op_check_obj, request.user.db_access)
                if add_comments_response.status_code != status.HTTP_201_CREATED:
                    DailyOperationalCheckUpdater.delete_daily_op_check(op_check_obj, request.user.db_access)
                    return add_comments_response
                
                engines=request.data.get("engines")
                if engines:
                    response=EngineHandler.handle_update_multiple(request.user,engines,op_check_obj)
                    if response.status_code!=status.HTTP_200_OK:
                        DailyOperationalCheckUpdater.delete_daily_op_check(op_check_obj,request.user.db_access)
                        return response

                # update fields after db entry has been made
                op_check_obj, update_status = DailyOperationalCheckUpdater.update_op_check_post_creation(op_check_obj, request.user)
                if update_status.status_code != status.HTTP_202_ACCEPTED:
                    return update_status

                # create daily check record
                db_name = request.user.db_access
                detailed_user = UserHelper.get_detailed_user_obj(request.user.email, db_name)
                company_name = detailed_user.company.company_name
                channel_name = company_name
                pusher_payload = {'location': op_check_obj.location.location_id}
                history_func = OperatorCheckHistory.create_daily_check_record_by_obj
                pusher_helper = PusherHelper(channel_name, PusherHelper.OpCheckDoneEvent, pusher_payload, False, history_func)
                if(not pusher_helper.push(op_check_obj)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_12))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_12), status=status.HTTP_400_BAD_REQUEST)

                # update asset fields
                asset, update_response = AssetUpdater.update_usage(serializer.validated_data.get("VIN"), serializer.validated_data.get("mileage"), serializer.validated_data.get("hours"), db_name)
                if update_response.status_code != status.HTTP_200_OK:
                    return update_response

                # create asset event log
                description = "Operator check " + str(op_check_obj.custom_id) + " was added. " + DailyOperationalCheckHelper.generate_op_check_metrics_string(op_check_obj, db_name)
                event_log_response = OperatorCheckHistory.create_operator_check_event_log(op_check_obj, description)
                if event_log_response.status_code != status.HTTP_201_CREATED:
                    return event_log_response

                # check to see if the status needs to be updated
                if(serializer.validated_data.get("is_tagout")):
                    AssetUpdater.update_asset_status(serializer.validated_data.get("VIN"), AssetModel.Inop)
                    # create asset event log
                    description = "Asset was set to inoperative due to operator check " + str(op_check_obj.custom_id) + "."
                    event_log_response = OperatorCheckHistory.create_operator_check_event_log(op_check_obj, description)
                    if event_log_response.status_code != status.HTTP_201_CREATED:
                        return event_log_response

                # create asset record 
                if(not AssetHistory.create_asset_record(serializer.validated_data.get("VIN"), db_name)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

                if DailyOperationalCheckHelper.check_operational_check_issues(request.data.get("data")):
                    # ----------------- Email Managers since issues were found-------------------
                    notification_config, resp = NotificationHelper.get_notification_config_by_name("New Daily Check", db_name)
                    if resp.status_code != status.HTTP_302_FOUND:
                        return resp
                    if notification_config.active and (
                        notification_config.triggers is None or (
                            "add_daily_check" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                        )
                    ):
                        htmlMessage = PdfManager.gen_daily_op_check_notification_email(
                            op_check_obj,
                            request.data.get("data"),
                            DailyOperationalCheckHelper.get_checks_from_request_data(request.data.get("data")),
                            notification_config,
                            request.user
                        )
                        email_title = "Issues Found in Daily Operational Check for " + str(op_check_obj.VIN) + " - Auto-Generated email"

                        if notification_config.recipient_type == "auto":
                            recipients = list(AssetHelper.get_asset_managers_emails(str(op_check_obj.VIN), db_name))
                        else:
                            recipients = NotificationHelper.get_recipients_for_notification(notification_config, db_name)

                        email_response = Email.send_email_notification(recipients, email_title, htmlMessage, [], html_content=True)

                        if email_response.status_code != status.HTTP_200_OK:
                            return email_response
                
                return Response(status=status.HTTP_201_CREATED)

            Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, serializer.errors))
            return Response(CustomError.get_full_error_json(CustomError.S_0, serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
        
    @staticmethod
    def handle_get_daily_operational_checks_by_VIN(vin, user):
        try:
            daily_op_checks, search_response = DailyOperationalCheckHelper.get_operational_checks_by_vin(vin, user.db_access)
            if search_response.status_code != status.HTTP_302_FOUND:
                return search_response 
            relevant_daily_op_checks = DailyOperationalCheckHelper.select_related_to_daily_check(DailyOperationalCheckHelper.filter_daily_operational_checks_for_user(daily_op_checks, user))
            daily_check_id_list = relevant_daily_op_checks.values_list('daily_check_id', flat=True)
            serializer = LightAssetDailyChecksSerializer(relevant_daily_op_checks, many=True,
            context=DailyOperationalCheckHelper.get_daily_check_ser_context(daily_check_id_list, user))
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_daily_operational_check_details_by_id(op_check_id, user):
        try:
            daily_op_check, search_response = DailyOperationalCheckHelper.get_daily_operators_check_by_id(op_check_id, user.db_access)
            if search_response.status_code != status.HTTP_302_FOUND:
                return search_response 

            serializer = LightAssetDailyChecksSerializer(daily_op_check,
            context=DailyOperationalCheckHelper.get_daily_check_ser_context([daily_op_check.daily_check_id], user))
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_daily_operational_check_details_by_custom_id(custom_op_check_id, user):
        try:
            daily_op_check, search_response = DailyOperationalCheckHelper.get_daily_operators_check_by_custom_id(custom_op_check_id, user.db_access)
            if search_response.status_code != status.HTTP_302_FOUND:
                return search_response

            serializer = LightAssetDailyChecksSerializer(daily_op_check,
            context=DailyOperationalCheckHelper.get_daily_check_ser_context([daily_op_check.daily_check_id], user))
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
    
    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_all_assets_with_no_check(user):
        try:
            db_name = user.db_access

            today_start, today_end = HelperMethods.get_datetime_range_for_today()
            vins_with_op_check_today = DailyOperationalCheckHelper.get_daily_checks_for_daterange(today_start,
                                                                                                  today_end,
                                                                                                  db_name)
            vins_with_op_check_today = vins_with_op_check_today.values_list('VIN', flat=True)

            assets_with_no_check_today = AssetHelper.select_related_to_asset(
                AssetHelper.get_assets_not_in_VIN_list_and_active(vins_with_op_check_today, user.db_access))

            relevant_assets = AssetHelper.filter_assets_for_daily_checks_for_user(assets_with_no_check_today, user)
            context = AssetHelper.get_serializer_context_2(relevant_assets, user)
            serializer = LightAssetModelSerializer(relevant_assets, many=True, context=context)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_daily_operator_check(request_data, user):
        try:
            # get daily operator check
            daily_op_check, daily_op_check_response = DailyOperationalCheckHelper.get_daily_operators_check_by_id(request_data.get("daily_op_check_id"), user.db_access)
            if daily_op_check_response.status_code != status.HTTP_302_FOUND:
                return daily_op_check_response
            
            engines=request_data.get("engines")
            if engines:
                response=EngineHandler.handle_update_multiple(user,engines,daily_op_check)
                if response.status_code!=status.HTTP_200_OK:
                    return response

            if not AssetHelper.check_asset_status_active(daily_op_check.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            # update daily operator check
            updated_daily_op_check, old_values, is_important, update_daily_op_check_response = DailyOperationalCheckUpdater.update_daily_operator_check(daily_op_check, request_data, user)
            if update_daily_op_check_response.status_code != status.HTTP_202_ACCEPTED:
                return update_daily_op_check_response

            if is_important:
                # ----------------- Email Vendor -------------------
                notification_config, resp = NotificationHelper.get_notification_config_by_name("Updated Daily Check", user.db_access)
                if resp.status_code != status.HTTP_302_FOUND:
                    return resp
                if notification_config.active and (
                    notification_config.triggers is None or (
                        "update_daily_check" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                    )
                ):
                    htmlMessage = PdfManager.gen_updated_daily_ops_check_report(
                        daily_op_check,
                        updated_daily_op_check,
                        old_values,
                        notification_config,
                        user
                    )
                    email_title = "Daily Operational Check (ID " + str(updated_daily_op_check.daily_check_id) + ") Has Been Updated - Auto-Generated Email"

                    if notification_config.recipient_type == "auto":
                        recipients = UserHelper.get_managers_emails_by_location(user.db_access, [DailyOperationalCheckHelper.get_daily_check_location(updated_daily_op_check)])
                    else:
                        recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access)

                    email_response = Email.send_email_notification(recipients, email_title, htmlMessage, [], html_content=True)
                    if email_response.status_code != status.HTTP_200_OK:
                        return email_response
                # --------------------------------------------------
                    
            # There is potential that mileage and/or hours might be changed. In this case we may want to update the 
            # the asset's mileage/hours based on the updated value IF this daily check is the latest process associated
            # with this asset.

            # create daily check record
            if(not OperatorCheckHistory.create_daily_check_record_by_obj(updated_daily_op_check)):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_12))
                return Response(CustomError.get_full_error_json(CustomError.MHF_12), status=status.HTTP_400_BAD_REQUEST)

            # create asset event log
            description = "Operator check " + str(updated_daily_op_check.custom_id) + " was updated."
            event_log_response = OperatorCheckHistory.create_operator_check_event_log(updated_daily_op_check, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            updated_daily_op_check.save()

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
        
        
