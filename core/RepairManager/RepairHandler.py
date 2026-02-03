from core.PusherManager.PusherHelper import PusherHelper
from api.Models.repair_file import RepairFile
from api.Models.Company import Company
from core.IssueManager.IssueHelper import IssueHelper
from core.IssueManager.IssueHandler import IssueUpdater
from api.Serializers.serializers import IssueSerializer
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .RepairHelper import RepairHelper
from .RepairUpdater import RepairUpdater
from ..AssetManager.AssetUpdater import AssetUpdater
from ..AssetManager.AssetHelper import AssetHelper
from ..HistoryManager.AssetHistory import AssetHistory
from ..HistoryManager.IssueHistory import IssueHistory
from ..HistoryManager.RepairHistory import RepairHistory
from ..FileManager.PdfManager import PdfManager
from ..Helper import HelperMethods
from ..DisposalManager.DisposalHelper import DisposalHelper
from ..TransferManager.TransferHelper import TransferHelper
from ..UserManager.UserHelper import UserHelper
from ..BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from ..NotificationManager.NotificationHelper import NotificationHelper
from ..IssueManager.IssueHandler import IssueHandler
from communication.EmailService.EmailService import Email
from api.Serializers.serializers import RepairSerializer, LightRepairSerializer, LightAssetModelSerializer
from api.Models.repairs import RepairsModel
from api.Models.asset_model import AssetModel
from api.Models.asset_issue import AssetIssueModel
from api.Models.DetailedUser import DetailedUser
from GSE_Backend.errors.ErrorDictionary import CustomError
from datetime import datetime
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class RepairHandler ():
    
    @staticmethod
    def handle_add_repairs(data, file_specs, files, user):
        # Check to see if the request has the fields required by the asset
        check_status = RepairHelper.check_request_info_present(data, user.db_access)
        asset_obj = AssetHelper.get_asset_by_VIN(data.get('repair_data').get("VIN"), user.db_access)

        if not AssetHelper.check_asset_status_active(asset_obj.VIN, user.db_access):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                               CustomError.get_error_user(CustomError.TUF_16)))
            return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                            CustomError.get_error_user(CustomError.TUF_16)),
                            status=status.HTTP_400_BAD_REQUEST)

        if check_status.status_code != status.HTTP_200_OK:
            return check_status
            
        if('repair_data' in data and 'assetissuemodel_set' in data):
            requested_data = data.get('repair_data', [])
            ser = RepairSerializer(data=requested_data)
            assetissuemodel_set_dict = data.get('assetissuemodel_set', [])
            issues = assetissuemodel_set_dict["issue_set"]

            if(ser.is_valid()):

                repair_obj = ser.save()
                db_name = user.db_access
                detailed_user = UserHelper.get_detailed_user_obj(user.email, db_name)

                # update fields after db entry has been made
                repair_obj, update_status = RepairUpdater.update_repair_request_post_creation(repair_obj, detailed_user)
                if update_status.status_code != status.HTTP_202_ACCEPTED:
                    return update_status

                # ----------- Add Issues to Repair Request -----------
                issues_in_repair = list()
                is_accident = None
                for issue in issues:
                    try:
                        asset_issue_obj = AssetIssueModel.objects.get(issue_id=issue)
                        # Check if issue is already a part of a repair request
                        if(asset_issue_obj.repair_id is not None):
                            errorMessage = "Issue id " + str(asset_issue_obj.issue_id) + " is already in repair request id " + str(asset_issue_obj.repair_id.repair_id)
                            Logger.getLogger().error(errorMessage)
                            RepairsModel.objects.using(db_name).filter(repair_id=repair_obj.repair_id).delete()
                            return Response(CustomError.get_full_error_json(CustomError.DR_0), status=status.HTTP_400_BAD_REQUEST)
                        # Check if VIN for each issue matches repair order VIN --> If not then return 400
                        if(ser.validated_data.get("VIN") != asset_issue_obj.VIN):
                            errorMessage = "Issue id " + str(asset_issue_obj.issue_id) + " has non matching VIN (" + str(asset_issue_obj.VIN) + ") with repair VIN (" + str(ser.validated_data.get("VIN")) + ")"
                            Logger.getLogger().error(errorMessage)
                            RepairsModel.objects.using(db_name).filter(repair_id=repair_obj.repair_id).delete()
                            return Response(CustomError.get_full_error_json(CustomError.IDNM_0), status=status.HTTP_400_BAD_REQUEST)
                        # Check if issue is result of accident and if that differs from previous issue --> If it differs return 400
                        if is_accident is not None and is_accident != IssueHelper.is_result_of_accident(asset_issue_obj):
                            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IIR_0))
                            RepairsModel.objects.using(db_name).filter(repair_id=repair_obj.repair_id).delete()
                            return Response(CustomError.get_full_error_json(CustomError.IIR_0), status=status.HTTP_400_BAD_REQUEST)

                        is_accident = IssueHelper.is_result_of_accident(asset_issue_obj)
                        repair_obj.assetissuemodel_set.add(asset_issue_obj)
                        issues_in_repair.append(asset_issue_obj)

                        # create issue record
                        if(not IssueHistory.create_issue_record_by_obj(asset_issue_obj)):
                            Logger.getLogger().error(CustomError.MHF_4)
                            return Response(CustomError.get_full_error_json(CustomError.MHF_4), status=status.HTTP_400_BAD_REQUEST)

                        # create asset event log
                        description = "Issue " + str(asset_issue_obj.custom_id) + " was added to repair " + str(repair_obj.work_order) + "."
                        event_log_response = IssueHistory.create_issue_event_log(asset_issue_obj, description)
                        if event_log_response.status_code != status.HTTP_201_CREATED:
                            return event_log_response

                    except ObjectDoesNotExist:
                        RepairsModel.objects.using(db_name).filter(repair_id=repair_obj.repair_id).delete()
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.IDNE_0))
                        return Response(CustomError.get_full_error_json(CustomError.IDNE_0), status=status.HTTP_400_BAD_REQUEST)

                    except Exception as e:
                        RepairsModel.objects.using(db_name).filter(repair_id=repair_obj.repair_id).delete()
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
                        return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

                # ----------- If refurbishment create placeholder issue ---------------

                if repair_obj.is_refurbishment:
                    # TODO: Set the issue category to refurbishment
                    refurbish_issue_data = {
                        "VIN": repair_obj.VIN,
                        "issue_details": repair_obj.description, 
                        "issue_title": "Refurbishment",
                        "issue_type": AssetIssueModel.critical if repair_obj.is_urgent else AssetIssueModel.non_critical, 
                        "issue_result": AssetIssueModel.other,
                        "repair_id": repair_obj.repair_id,
                        "created_by": detailed_user.detailed_user_id,
                        "modified_by": detailed_user.detailed_user_id,
                    }

                    issue_response = IssueHandler.handle_add_issue(refurbish_issue_data, [], user)
                    if issue_response.status_code != status.HTTP_201_CREATED:
                        return issue_response
                # -------------------------------------------------------------------------

                # If everything is successful --> Add the repair to db
                repair_obj.save()

                # ------------ Add files to blob and db ------------
                upload_response = RepairHandler.handle_add_supporting_files(repair_obj, file_specs, files, user)
                if upload_response.status_code != status.HTTP_200_OK:
                    RepairUpdater.delete_repair_by_id(repair_obj.repair_id, user.db_access)
                    return upload_response
                # --------------------------------------------------

                # create repair record
                company_name = detailed_user.company.company_name
                channel_name = company_name
                pusher_payload = {'location': repair_obj.location.location_id}
                history_func = RepairHistory.create_repair_record_by_obj
                pusher_helper = PusherHelper(channel_name, PusherHelper.RepairCreatedEvent, pusher_payload, False, history_func)
                if(not pusher_helper.push(repair_obj, db_name)):
                    Logger.getLogger().error(CustomError.MHF_1)
                    return Response(CustomError.get_full_error_json(CustomError.MHF_1), status=status.HTTP_400_BAD_REQUEST)
               
                # update asset fields
                asset, update_response = AssetUpdater.update_usage(ser.validated_data.get("VIN"), requested_data.get("mileage"), requested_data.get("hours"), user.db_access)
                if update_response.status_code != status.HTTP_200_OK:
                    return update_response

                # create asset event log
                description = "Repair order " + str(repair_obj.work_order) + " was created."
                event_log_response = RepairHistory.create_repair_event_log(repair_obj, description)
                if event_log_response.status_code != status.HTTP_201_CREATED:
                    return event_log_response

                # if the pickup date is today then set asset to inop and last process to repair...
                if HelperMethods.datetime_is_today(repair_obj.available_pickup_date): 
                    # update asset status
                    AssetUpdater.update_asset_status(ser.validated_data.get("VIN"), AssetModel.Inop)
                    # update asset last process
                    AssetUpdater.update_last_process(ser.validated_data.get("VIN"), AssetModel.Repair)

                    # create asset event log
                    description = "Asset was set to inoperative and last proccess was set to " + str(AssetModel.Repair) + " " + str(repair_obj.work_order) + str(".")
                    event_log_response = RepairHistory.create_repair_event_log(repair_obj, description)
                    if event_log_response.status_code != status.HTTP_201_CREATED:
                        return event_log_response

                # create asset record 
                if(not AssetHistory.create_asset_record(ser.validated_data.get("VIN"), db_name)):
                    Logger.getLogger().error(CustomError.MHF_0)
                    return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)
                
                # ----------------- Email Vendor -------------------
                if not repair_obj.is_refurbishment:
                    notification_config, resp = NotificationHelper.get_notification_config_by_name("New Repair", user.db_access)
                    if resp.status_code != status.HTTP_302_FOUND:
                        return resp
                    if notification_config.active and (
                    notification_config.triggers is None or (
                        "add_repair" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                        )
                    ):
                        assetObj = AssetModel.objects.get(VIN=repair_obj.VIN)
                        fileInfo, htmlMessage, email_title = PdfManager.gen_repair_order_pdf(repair_obj, assetObj, issues_in_repair, notification_config, user)

                        if repair_obj.in_house:
                            if notification_config.recipient_type == "auto":
                                recipients = UserHelper.get_managers_emails_by_location(user.db_access, [RepairHelper.get_repair_location(repair_obj)])
                            else:
                                recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access)
                        else:
                            if notification_config.recipient_type == "auto":
                                recipients = []
                            else:
                                recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access)
                            recipients = recipients + [repair_obj.vendor_email]

                        if(fileInfo is not None):
                            email_response = Email.send_email_notification(recipients, email_title, htmlMessage, [fileInfo], html_content=True)
                        else:
                            email_response = Email.send_email_notification(recipients, email_title, htmlMessage, [], html_content=True)
                        if email_response.status_code != status.HTTP_200_OK: # If email not successful --> delete entry
                            RepairUpdater.delete_repair_by_id(repair_obj.repair_id, user.db_access)
                            return email_response
                # --------------------------------------------------

                return Response({"repair_id":repair_obj.repair_id},status=status.HTTP_200_OK)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors), status=status.HTTP_400_BAD_REQUEST)
        
        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.I_0))
            return Response(CustomError.get_full_error_json(CustomError.I_0), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_supporting_files(repair_obj, file_specs, request_files, user):
        try:
            file_entries = []
            for _file in request_files:
                file_purpose = None
                expiration_date = None
                for info in file_specs.get("file_info"):
                    if info.get("file_name") == _file.name:
                        file_purpose = info.get("purpose").lower()
                        expiration_date = info.get("expiration_date")
                        break
                if not RepairHelper.validate_purpose(file_purpose):
                    return Response(CustomError.get_full_error_json(CustomError.FUF_2), status=status.HTTP_400_BAD_REQUEST)

                # ------------ Upload files to blob --------------
                company_name = UserHelper.get_company_name_by_user_email(user.email, user.db_access)
                file_prefix = str(file_purpose.replace(" ", "_")) + "_" + str(repair_obj.repair_id) + "_"
                container = "repair"
                file_status, file_info = BlobStorageHelper.write_file_to_blob(_file, container, file_prefix, company_name, user.db_access)
                if(not file_status):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_0))
                    return Response(CustomError.get_full_error_json(CustomError.FUF_0), status=status.HTTP_400_BAD_REQUEST)

                # ------------ Create file entry -----------------
                detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
                file_entry = RepairUpdater.construct_repair_file_instance(repair_obj, file_info, file_purpose, expiration_date, detailed_user)

                file_entries.append(file_entry)

            # Upload file entries to db
            RepairFile.objects.using(user.db_access).bulk_create(file_entries)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_repairs_by_vin(_vin, user):
        try:
            queryset = RepairHelper.select_related_to_repair(RepairsModel.objects.using(user.db_access).filter(VIN__VIN=_vin))
            relevant_qs = RepairHelper.filter_repairs_for_user(queryset, user)
            repair_id_list = relevant_qs.values_list('repair_id', flat=True)
            ser = LightRepairSerializer(relevant_qs, many=True, context=RepairHelper.get_repair_ser_context(repair_id_list, user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------
    

    @staticmethod
    def handle_list_repairs(user):
        try:
            queryset = RepairHelper.select_related_to_repair(RepairsModel.objects.using(user.db_access).filter(status__in=RepairsModel.incomplete_status_values))
            relevant_qs = RepairHelper.filter_repairs_for_user(queryset, user)
            updated_queryset = RepairUpdater.update_repair_downtime(relevant_qs, user.db_access)
            repair_id_list = updated_queryset.values_list('repair_id', flat=True)
            ser = LightRepairSerializer(updated_queryset, many=True, context=RepairHelper.get_repair_ser_context(repair_id_list, user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_list_complete_repairs(user):
        try:
            queryset = RepairHelper.select_related_to_repair(RepairsModel.objects.using(user.db_access).filter(status__in=RepairsModel.complete_status_values))
            relevant_qs = RepairHelper.filter_repairs_for_user(queryset, user)
            repair_id_list = relevant_qs.values_list('repair_id', flat=True)
            ser = LightRepairSerializer(relevant_qs, many=True, context=RepairHelper.get_repair_ser_context(repair_id_list, user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_repair_delivered(repair_obj, date_updated, user):
        try:
            # Check if repair has cost entries
            if not RepairHelper.repair_has_cost(repair_obj.repair_id, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.RCDNE_0))
                return repair_obj, Response(CustomError.get_full_error_json(CustomError.RCDNE_0), status=status.HTTP_400_BAD_REQUEST)

            repair_obj.status = RepairsModel.delivered
            _status_updated_datetime = HelperMethods.datetime_string_to_datetime(date_updated)
            repair_obj.date_completed = _status_updated_datetime
            diff = HelperMethods.get_datetime_delta(start=repair_obj.date_created, end=_status_updated_datetime, delta_format="hours")
            repair_obj.down_time = diff
            
            # update asset status
            AssetUpdater.update_asset_status(repair_obj.VIN, AssetModel.Active)

            # create asset record 
            if(not AssetHistory.create_asset_record(repair_obj.VIN, user.db_access)):
                Logger.getLogger().error(CustomError.MHF_0)
                return repair_obj, Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            # create asset event log
            description = "Asset was set to active due to repair " + str(repair_obj.work_order) + " completion and delivery."
            event_log_response = RepairHistory.create_repair_event_log(repair_obj, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return repair_obj, event_log_response

            repair_obj.save()
            RepairUpdater.update_issues(repair_obj.repair_id, True, user.db_access)

            return repair_obj, Response(status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.RDNE_0))
            return repair_obj, Response(CustomError.get_full_error_json(CustomError.RDNE_0), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return repair_obj, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_repair_cancelled(repair_obj, user):
        try:
            # update the last process and status of the asset
            asset_obj = AssetHelper.get_asset_by_VIN(repair_obj.VIN, user.db_access)
            if asset_obj.last_process == AssetModel.Repair:
                prev_last_process = AssetHelper.get_previous_different_last_process(asset_obj, user.db_access)
                AssetUpdater.update_last_process(asset_obj.VIN, prev_last_process)
                description = "Asset last proccess was set to " + prev_last_process + " due to cancellation of repair " + str(repair_obj.work_order) + "."

                # only update the status of the asset if it was inoperative and prev status was active
                asset_prev_status = AssetHelper.get_previous_different_status(asset_obj, user.db_access)
                if asset_obj.status == AssetModel.Inop and asset_prev_status == AssetModel.Active:
                    AssetUpdater.update_asset_status(asset_obj.VIN, AssetModel.Active)
                    description = "Asset was set to active and last proccess was set to " + prev_last_process + " due to cancellation of repair " + str(repair_obj.work_order) + "."

                event_log_response = RepairHistory.create_repair_event_log(repair_obj, description)
                if event_log_response.status_code != status.HTTP_201_CREATED:
                    return repair_obj, event_log_response

            # set the repair object status to cancelled
            repair_obj.status = RepairsModel.cancelled
            repair_obj.save()

            # email vendor
            notification_config, resp = NotificationHelper.get_notification_config_by_name("Request Cancellation", user.db_access)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp
            if notification_config.active and (
                notification_config.triggers is None or (
                    "cancel_repair" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                )
            ):
                asset_location = repair_obj.VIN.current_location.location_name
                html_message, email_title = PdfManager.gen_request_cancellation_email(
                    "Repair",
                    repair_obj.work_order,
                    notification_config,
                    user,
                    asset_location
                )

                vendor_email = repair_obj.vendor_email
                if notification_config.recipient_type == "auto":
                    recipients = [vendor_email]
                else:
                    recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access) + [vendor_email]

                email_response = Email.send_email_notification(recipients, email_title, html_message, html_content=True)
                if email_response.status_code != status.HTTP_200_OK: # If email not successful, do nothing
                    pass

            # return the response - updated repair object
            return repair_obj, Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return repair_obj, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_repair_generic_status(repair_obj, new_status):
        try:
            repair_obj.status = new_status
            repair_obj.save()
            return repair_obj, Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_update_repair_status(request_data, user):
        try:
            new_status = str(request_data.get('status')).lower()

            # check if new status is valid
            if not RepairHelper.is_status_valid(new_status):
                Logger.getLogger().error(CustomError.IS_0)
                return Response(CustomError.get_full_error_json(CustomError.IS_0), status=status.HTTP_400_BAD_REQUEST)

            # get repair object
            repair_obj, repair_request_response = RepairHelper.get_repair_request_by_id(request_data.get('repair_id'), user.db_access)

            if not AssetHelper.check_asset_status_active(repair_obj.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            if repair_request_response.status_code != status.HTTP_302_FOUND:
                return repair_request_response

            original_status = str(repair_obj.status).lower()

            # check if new status is new
            if new_status == original_status:
                Logger.getLogger().error(CustomError.SNN_0)
                return Response(CustomError.get_full_error_json(CustomError.SNN_0), status=status.HTTP_400_BAD_REQUEST)

            # update status
            if new_status == RepairsModel.delivered.lower():
                repair_obj, update_response = RepairHandler.handle_repair_delivered(repair_obj, request_data.get('date_delivered'), user)
            elif new_status == RepairsModel.cancelled.lower():
                repair_obj, update_response = RepairHandler.handle_repair_cancelled(repair_obj, user)
            else:
                repair_obj, update_response = RepairHandler.handle_repair_generic_status(repair_obj, new_status)

            if update_response.status_code != status.HTTP_200_OK:
                return update_response

            # set modified_by
            repair_obj, modified_by_status = RepairUpdater.update_repair_request_modified_by(repair_obj, user)
            if modified_by_status.status_code != status.HTTP_202_ACCEPTED:
                return modified_by_status

            # mark issues as resolved / unresolved based on repair status, and pusher events for issues
            # incase repair was previously complete and delivered, revert status of related issues to unresolved.
            event_name = None
            count = 0
            pusher_payload = {'location': repair_obj.location.location_id, 'count': count}
            if original_status == RepairsModel.delivered.lower():
                repair_obj.date_completed = None
                repair_obj.save()
                count = AssetIssueModel.objects.filter(repair_id = repair_obj.repair_id, is_resolved = True).count() 
                RepairUpdater.update_issues(repair_obj.repair_id, False, user.db_access)
                pusher_payload = {'location': repair_obj.location.location_id, 'count': count}
                event_name = PusherHelper.IssueUnresolvedEvent
            elif new_status == RepairsModel.delivered.lower():
                count = AssetIssueModel.objects.filter(repair_id = repair_obj.repair_id, is_resolved = False).count()
                RepairUpdater.update_issues(repair_obj.repair_id, True, user.db_access)
                pusher_payload = {'location': repair_obj.location.location_id, 'count': count}
                event_name = PusherHelper.IssueResolvedEvent
            
            skip_push = False
            if event_name is None:
                skip_push =  True
            channel_name = DetailedUser.objects.get(email=user.email).company.company_name
            history_func = RepairHistory.create_repair_event_log
            pusher_helper = PusherHelper(channel_name, event_name, pusher_payload, skip_push, history_func)
            
            # create asset event log
            description = "Repair " + str(repair_obj.work_order) + " status was set to " + new_status + "."
            event_log_response = pusher_helper.push(repair_obj, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            # -------------- Pusher for repair events -----------------
            event_name = None
            pusher_payload = {'location': repair_obj.location.location_id}
            # check if repair was cancelled
            if repair_obj.status in [RepairsModel.cancelled.lower(),RepairsModel.denied.lower()]:
                event_name = PusherHelper.RepairCancelledEvent
            # check if a repair that was originally complete is marked as incomplete
            elif original_status in RepairsModel.complete_status_values and repair_obj.status not in RepairsModel.complete_status_values:
                event_name = PusherHelper.RepairIncompleteEvent
            # check if a repair that was originally incomplete is marked as complete
            elif original_status not in RepairsModel.complete_status_values and repair_obj.status in RepairsModel.complete_status_values:
                event_name = PusherHelper.RepairCompleteEvent

            skip_push = False
            if new_status in RepairsModel.complete_status_values and original_status in RepairsModel.complete_status_values:
                skip_push = True
            if new_status not in RepairsModel.complete_status_values and original_status not in RepairsModel.complete_status_values:
                skip_push = True
            
            channel_name = DetailedUser.objects.get(email=user.email).company.company_name
            history_func = RepairHistory.create_repair_record_by_obj
            pusher_helper = PusherHelper(channel_name, event_name, pusher_payload, skip_push, history_func)

            # create repair history record and send a pusher event
            if event_name is not None:
                if not pusher_helper.push(repair_obj, user.db_access):
                    Logger.getLogger().error(CustomError.MHF_1)
                    return Response(CustomError.get_full_error_json(CustomError.MHF_1), status=status.HTTP_400_BAD_REQUEST)
            # ---------------------------------------
            
            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_vendor(request_data, user):
        rep_id = request_data.get("repair_id")
        vendor_id = request_data.get("vendor_id")
        try:

            repair_obj = RepairsModel.objects.using(user.db_access).get(pk=rep_id)
            repair_obj.vendor_id = vendor_id

            if not AssetHelper.check_asset_status_active(repair_obj.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            repair_obj.save()

            # set modified_by
            repair_obj, modified_by_status = RepairUpdater.update_repair_request_modified_by(repair_obj, user)
            if modified_by_status.status_code != status.HTTP_202_ACCEPTED:
                return modified_by_status

            # create repair record
            if(not RepairHistory.create_repair_record_by_obj(repair_obj, user.db_access)):
                Logger.getLogger().error(CustomError.MHF_1)
                return Response(CustomError.get_full_error_json(CustomError.MHF_1), status=status.HTTP_400_BAD_REQUEST)

            # create asset event log
            description = "Repair " + str(repair_obj.work_order) + " vendor was changed to " + str(repair_obj.vendor.vendor_name) + "."
            event_log_response = RepairHistory.create_repair_event_log(repair_obj, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_unresolved_repairs_count(user):
        try:
            queryset = RepairsModel.objects.using(user.db_access).exclude(status__in=[RepairsModel.delivered,RepairsModel.cancelled,RepairsModel.denied])
            count = RepairHelper.filter_repairs_for_user(queryset, user).count()
            return Response({"count":count}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_resolved_repairs_count(user):
        try:
            queryset = RepairsModel.objects.using(user.db_access).filter(status__in=[RepairsModel.delivered,RepairsModel.cancelled,RepairsModel.denied])
            count = RepairHelper.filter_repairs_for_user(queryset, user).count()
            return Response({"count":count}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_repair_percentage_resolved(user):
        try:
            total_qs = RepairsModel.objects.using(user.db_access).all()
            count_total = RepairHelper.filter_repairs_for_user(total_qs, user).count()
            complete_qs = RepairsModel.objects.filter(status=RepairsModel.complete)
            count_complete = RepairHelper.filter_repairs_for_user(complete_qs, user).count()
            percentageResolved = round((count_complete / count_total) * 100, 2)
            return Response({"resolved_percent":percentageResolved}, status=status.HTTP_200_OK)
        except ZeroDivisionError as zde:
            Logger.getLogger().error(zde)
            return Response({"resolved_percent":0}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_replacement_suggestions(_vin, user):
        try:
            replacements_by_mileage, replacements_by_hours = AssetHelper.get_similar_assets(_vin, user.db_access)
            if replacements_by_mileage is None or replacements_by_hours is None:
                return Response("Error retrieving similar assets", status=status.HTTP_400_BAD_REQUEST)
            
            all_assets = AssetHelper.get_all_assets(user.db_access)
            context = AssetHelper.get_serializer_context_2(all_assets,user)
            serializer_by_mileage = LightAssetModelSerializer(replacements_by_mileage, many=True, context=context)
            serializer_by_hours = LightAssetModelSerializer(replacements_by_hours, many=True, context=context)
            return Response({
                "replacements_ordered_by_mileage": serializer_by_mileage.data,
                "replacements_ordered_by_hours": serializer_by_hours.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_repair_detail_by_id(repair_id, user):
        try:
            repair_request, repair_request_response = RepairHelper.get_repair_request_by_id(repair_id, user.db_access)
            if repair_request_response.status_code != status.HTTP_302_FOUND:
                return repair_request_response
            serializer = LightRepairSerializer(repair_request, context=RepairHelper.get_repair_ser_context([repair_request.repair_id], user.db_access))
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_repair_detail_by_work_order(work_order, user):
        try:
            repair_request, repair_request_response = RepairHelper.get_repair_request_by_work_order(work_order, user.db_access)
            if repair_request_response.status_code != status.HTTP_302_FOUND:
                return repair_request_response
            serializer = LightRepairSerializer(repair_request, context=RepairHelper.get_repair_ser_context([repair_request.repair_id], user.db_access))
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_repair(request_data, user):
        try:
            # get repair
            repair_request, repair_request_response = RepairHelper.get_repair_request_by_id(request_data.get("repair_id"), user.db_access)
            if repair_request_response.status_code != status.HTTP_302_FOUND:
                return repair_request_response
            if not AssetHelper.check_asset_status_active(repair_request.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)
            # update repair
            updated_repair_request, is_important, update_repair_request_response = RepairUpdater.update_repair_fields(repair_request, request_data, user)
            if update_repair_request_response.status_code != status.HTTP_202_ACCEPTED:
                return update_repair_request_response
            # create repair record
            if(not RepairHistory.create_repair_record_by_obj(updated_repair_request, user.db_access)):
                Logger.getLogger().error(CustomError.MHF_1)
                return Response(CustomError.get_full_error_json(CustomError.MHF_1), status=status.HTTP_400_BAD_REQUEST)

            # issues for repair
            issues = IssueHelper.get_issue_by_repair_id(updated_repair_request.repair_id, user.db_access)

            if is_important:
                # ----------------- Email Vendor -------------------
                notification_config, resp = NotificationHelper.get_notification_config_by_name("New Repair", user.db_access)
                if resp.status_code != status.HTTP_302_FOUND:
                    return resp
                if notification_config.active and (
                    notification_config.triggers is None or (
                        "update_repair" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                    )
                ):
                    asset_obj = AssetModel.objects.get(VIN=repair_request.VIN)
                    file_info, html_message, email_title = PdfManager.gen_repair_order_pdf(updated_repair_request, asset_obj, issues, notification_config, user, is_update=True)
                    if repair_request.in_house:
                        if notification_config.recipient_type == "auto":
                            recipients = UserHelper.get_managers_emails_by_location(user.db_access, [RepairHelper.get_repair_location(updated_repair_request)])
                        else:
                            recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access)
                    else:
                        if notification_config.recipient_type == "auto":
                            managers = UserHelper.get_managers_emails_by_location(user.db_access, [RepairHelper.get_repair_location(updated_repair_request)])
                            manager_list = [manager for manager in managers]
                            recipients = manager_list + [repair_request.vendor_email]   
                        else:
                            recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access)
                            recipients = recipients + [repair_request.vendor_email]   
            
                    if(file_info is not None):
                        email_response = Email.send_email_notification(recipients, email_title, html_message, [file_info], html_content=True)
                    else:
                        email_response = Email.send_email_notification(recipients, email_title, html_message, [], html_content=True)
                    if email_response.status_code != status.HTTP_200_OK:
                        return email_response
                # --------------------------------------------------
                
            # create asset event log
            description = "Repair " + str(updated_repair_request.work_order) + " was updated."
            event_log_response = RepairHistory.create_repair_event_log(updated_repair_request, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            updated_repair_request.save()

            return Response(status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    
