from core.PusherManager.PusherHelper import PusherHelper
from rest_framework.response import Response
from rest_framework import status
from api.Models.DetailedUser import DetailedUser
from api.Models.maintenance_request import MaintenanceRequestModel
from api.Models.maintenance_request_file import MaintenanceRequestFile
from api.Models.asset_model import AssetModel
from api.Models.inspection_type import InspectionTypeModel
from api.Models.asset_log import AssetLog
from ..InspectionTypeManager.InspectionTypeHelper import InspectionTypeHelper
from ..AssetManager.AssetUpdater import AssetUpdater
from ..AssetManager.AssetHelper import AssetHelper
from ..HistoryManager.AssetHistory import AssetHistory
from ..HistoryManager.MaintenanceHistory import MaintenanceHistory
from ..FileManager.PdfManager import PdfManager
from communication.EmailService.EmailService import Email
from .MaintenanceUpdater import MaintenanceUpdater
from .MaintenanceHelper import MaintenanceHelper
from ..UserManager.UserHelper import UserHelper
from ..DisposalManager.DisposalHelper import DisposalHelper
from ..TransferManager.TransferHelper import TransferHelper
from ..UserManager.UserHelper import UserHelper
from ..NotificationManager.NotificationHelper import NotificationHelper
from ..Helper import HelperMethods

from api.Serializers.serializers import MaintenanceRequestSerializer, LightMaintenanceRequestSerializer, InspectionTypeSerializer
from GSE_Backend.errors.ErrorDictionary import CustomError
from core.BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from multiprocessing.pool import ThreadPool
from datetime import datetime
import time
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class MaintenanceHandler():

    @staticmethod
    def handle_add_batch_maintenance_request(request_data, files, user):
        try:
            db_name = user.db_access
            # Check to see if the request has the fields required by the asset, if any asset is disposed of
            check_status = MaintenanceHelper.check_request_info_present(request_data, db_name)
            if check_status.status_code != status.HTTP_200_OK:
                return check_status

            for request in request_data.get('assets'):
                if not AssetHelper.check_asset_status_active(request.get("VIN"), db_name):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                       CustomError.get_error_user(CustomError.TUF_16)))
                    return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                    CustomError.get_error_user(CustomError.TUF_16)),
                                    status=status.HTTP_400_BAD_REQUEST)

            maint_req_list = MaintenanceHelper.update_batch_maintenance_dict(request_data.get("assets"), db_name)
            
            # check if the input body has same location ID
            location_status = MaintenanceHelper.check_location_info(maint_req_list, db_name)
            if location_status.status_code != status.HTTP_200_OK:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.LDNM_0))
                return Response(CustomError.get_full_error_json(CustomError.LDNM_0), status=status.HTTP_400_BAD_REQUEST)

            ser = MaintenanceRequestSerializer(data=maint_req_list, many=True)

            if(ser.is_valid()):
                maintenance_objects = ser.save()
                
                # update fields after db entries have been made
                maintenance_objects, update_status = MaintenanceUpdater.batch_update_maintenance_request_post_creation(maintenance_objects, user)
                if update_status.status_code != status.HTTP_202_ACCEPTED:
                    return update_status

                # create maintenance records
                detailed_user = UserHelper.get_detailed_user_obj(user.email, db_name)
                company_name = detailed_user.company.company_name
                channel_name = company_name
                pusher_payload = {'location': None, 'count': len(maint_req_list)}
                history_func = MaintenanceHistory.create_maintenance_records
                pusher_helper = PusherHelper(channel_name, PusherHelper.MaintenanceCreatedEvent, pusher_payload, False, history_func)
                if(not pusher_helper.push(maintenance_objects)):
                    Logger.getLogger().error(CustomError.MHF_2)
                    return Response(CustomError.get_full_error_json(CustomError.MHF_2), status=status.HTTP_400_BAD_REQUEST)

                maintenance_by_vin = {maintenance.VIN.VIN: maintenance for maintenance in maintenance_objects}
                files_by_name = {file.name: file for file in files}

                def update_asset_and_upload_files(maint_req):
                    # update asset fields
                    asset, update_response = AssetUpdater.update_usage(maint_req.get("VIN"), maint_req.get("mileage"), maint_req.get("hours"), db_name)
                    if update_response.status_code != status.HTTP_200_OK:
                        return update_response

                    # upload files associated with the maintenance request
                    relevant_files = []
                    for file_info in maint_req.get("file_info", []):
                        relevant_files.append(files_by_name[file_info['file_name']])
                    if len(relevant_files) > 0:
                        maintenance_obj = maintenance_by_vin[maint_req.get("VIN")]
                        response = MaintenanceHandler.handle_add_supporting_files(maintenance_obj.maintenance_id, maint_req, relevant_files, user)
                        if response.status_code != status.HTTP_200_OK:
                            MaintenanceUpdater.delete_failed_maintenance_requests(maintenance_objects, db_name)
                            return response

                with ThreadPool(processes=int(10 if len(maint_req_list) > 10 else len(maint_req_list))) as pool:
                    pool.map(update_asset_and_upload_files, maint_req_list)

                # create asset event logs
                event_logs_response = MaintenanceHistory.create_added_maintenance_event_logs(maintenance_objects)
                if event_logs_response.status_code != status.HTTP_201_CREATED:
                    return event_logs_response

                def check_pickup_and_create_asset_record(maint_req_obj):
                    # if the pickup date is today then set asset to inop and last process to maintenance...
                    if HelperMethods.datetime_is_today(maint_req_obj.available_pickup_date):
                        AssetModel.objects.using(db_name).filter(
                            pk=maint_req_obj.VIN).update(
                                status=AssetModel.Inop,
                                last_process=AssetModel.Maintenance
                            )
                        # create asset event log
                        description = "Asset was set to inoperative and last proccess was set to " + str(AssetLog.maintenance) + " " + str(maint_req_obj.work_order) + "."
                        event_log_response = MaintenanceHistory.create_maintenance_event_log(maint_req_obj, description)
                        if event_log_response.status_code != status.HTTP_201_CREATED:
                            return event_log_response
                        
                            
                    # create asset record 
                    if(not AssetHistory.create_asset_record(maint_req_obj.VIN, db_name)):
                        Logger.getLogger().error(CustomError.MHF_0)
                        return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

                with ThreadPool(processes=int(10 if len(maintenance_objects) > 10 else len(maintenance_objects))) as pool:
                    pool.map(check_pickup_and_create_asset_record, maintenance_objects)

                # -------------- Email maintenance request(s) ---------------
                notification_config, resp = NotificationHelper.get_notification_config_by_name("New Maintenance", user.db_access)
                if resp.status_code != status.HTTP_302_FOUND:
                    return resp
                if notification_config.active and (
                    notification_config.triggers is None or (
                        "add_maintenance" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                    )
                ):
                    fileInfo, htmlMessage = PdfManager.gen_maintenance_pdf_request(maintenance_objects, notification_config, user)
                    email_title = "New Maintenance Request(s) - Auto-Generated Email"

                    if maintenance_objects[0].in_house:
                        if notification_config.recipient_type == "auto":
                            recipients = UserHelper.get_managers_emails_by_location(db_name, [MaintenanceHelper.get_maintenance_location(maintenance_objects[0])])
                        else:
                            recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access)
                    else:
                        recipients = [maintenance_objects[0].vendor_email]   
                        if notification_config.recipient_type != "auto":
                            recipients = recipients + NotificationHelper.get_recipients_for_notification(notification_config, user.db_access)

                    if(fileInfo is not None):
                        email_response = Email.send_email_notification(recipients, email_title, htmlMessage, [fileInfo], html_content=True)
                    else:
                        email_response = Email.send_email_notification(recipients, email_title, htmlMessage, [], html_content=True)
                    if email_response.status_code != status.HTTP_200_OK:
                        MaintenanceUpdater.delete_failed_maintenance_requests(maintenance_objects, db_name)
                        return email_response
                # -----------------------------------------------------------

                return Response(status=status.HTTP_201_CREATED)
            
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
            return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors), status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_maintenance_delivered(maintenance_obj, user):
        try:
            # Check that maintenance VIN exists
            if not AssetHelper.asset_exists(maintenance_obj.VIN, user.db_access):
                Logger.getLogger().error(CustomError.VDNE_0)
                return maintenance_obj, Response(CustomError.get_full_error_json(CustomError.VDNE_0), status=status.HTTP_400_BAD_REQUEST)

            # Update maintenance values
            asset_obj = AssetModel.objects.using(user.db_access).get(pk=maintenance_obj.VIN)
            maintenance_obj.status = MaintenanceRequestModel.complete
            maintenance_obj.date_completed = datetime.utcnow()
            maintenance_obj.mileage = asset_obj.mileage
            maintenance_obj.hours = asset_obj.hours
            maintenance_obj.save()

            AssetUpdater.update_asset_status(maintenance_obj.VIN, AssetModel.Active)
            
            # create asset record 
            if(not AssetHistory.create_asset_record(maintenance_obj.VIN, user.db_access)):
                Logger.getLogger().error(CustomError.MHF_0)
                return maintenance_obj, Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            # create asset event log
            description = "Asset was set to active due to maintenance " + str(maintenance_obj.work_order) + " completion and delivery."
            event_log_response = MaintenanceHistory.create_maintenance_event_log(maintenance_obj, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return maintenance_obj, event_log_response

            return maintenance_obj, Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return maintenance_obj, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_maintenance_cancelled(maintenance_obj, user):
        try:
            # update the last process and status of the asset
            asset_obj = AssetHelper.get_asset_by_VIN(maintenance_obj.VIN, user.db_access)
            if asset_obj.last_process == AssetModel.Maintenance:
                prev_last_process = AssetHelper.get_previous_different_last_process(asset_obj, user.db_access)
                AssetUpdater.update_last_process(asset_obj.VIN, prev_last_process)
                description = "Asset last proccess was set to " + prev_last_process + " due to cancellation of maintenance " + str(maintenance_obj.work_order) + "."

                # only update the status of the asset if it was inoperative and prev status was active
                asset_prev_status = AssetHelper.get_previous_different_status(asset_obj, user.db_access)
                if asset_obj.status == AssetModel.Inop and asset_prev_status == AssetModel.Active:
                    AssetUpdater.update_asset_status(asset_obj.VIN, AssetModel.Active)
                    description = "Asset was set to active and last proccess was set to " + prev_last_process + " due to cancellation of maintenance " + str(maintenance_obj.work_order) + "."

                event_log_response = MaintenanceHistory.create_maintenance_event_log(maintenance_obj, description)
                if event_log_response.status_code != status.HTTP_201_CREATED:
                    return maintenance_obj, event_log_response

            # set the maintenance object status to cancelled
            maintenance_obj.status = MaintenanceRequestModel.cancelled
            maintenance_obj.save()

            # email vendor
            notification_config, resp = NotificationHelper.get_notification_config_by_name("Request Cancellation", user.db_access)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp
            if notification_config.active and (
                notification_config.triggers is None or (
                    "cancel_maintenance" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                )
            ):
                asset_location = maintenance_obj.VIN.current_location.location_name
                html_message, email_title = PdfManager.gen_request_cancellation_email(
                    "Maintenance",
                    maintenance_obj.work_order,
                    notification_config,
                    user,
                    asset_location
                )

                vendor_email = maintenance_obj.vendor_email
                if notification_config.recipient_type == "auto":
                    recipients = [vendor_email]
                else:
                    recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access) + [vendor_email]

                email_response = Email.send_email_notification(recipients, email_title, html_message, html_content=True)
                if email_response.status_code != status.HTTP_200_OK: # If email not successful, do nothing
                    pass

            # return the response - updated maintenance object
            return maintenance_obj, Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return maintenance_obj, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_maintenance_generic_status(maintenance_obj, new_status):
        try:
            maintenance_obj.status = new_status
            maintenance_obj.save()
            return maintenance_obj, Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_update_maintenance_status(request_data, user):
        try:
            new_status = str(request_data.get('status')).lower()

            # check if new status is valid
            if not MaintenanceHelper.is_status_valid(new_status):
                Logger.getLogger().error(CustomError.IS_0)
                return Response(CustomError.get_full_error_json(CustomError.IS_0), status=status.HTTP_400_BAD_REQUEST)

            # get maintenance object
            maintenance_obj, maintenance_request_response = MaintenanceHelper.get_maintenance_request_by_id(request_data.get('maintenance_id'), user.db_access)
            if maintenance_request_response.status_code != status.HTTP_302_FOUND:
                return maintenance_request_response

            if not AssetHelper.check_asset_status_active(maintenance_obj.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            original_status = str(maintenance_obj.status).lower()

            # check if new status is new
            if new_status == original_status:
                Logger.getLogger().error(CustomError.SNN_0)
                return Response(CustomError.get_full_error_json(CustomError.SNN_0), status=status.HTTP_400_BAD_REQUEST)

            # update status
            if new_status == MaintenanceRequestModel.delivered.lower():
                maintenance_obj, update_response = MaintenanceHandler.handle_maintenance_delivered(maintenance_obj, user)
            if new_status == MaintenanceRequestModel.cancelled.lower():
                maintenance_obj, update_response = MaintenanceHandler.handle_maintenance_cancelled(maintenance_obj, user)
            else:
                maintenance_obj, update_response = MaintenanceHandler.handle_maintenance_generic_status(maintenance_obj, new_status)

            if update_response.status_code != status.HTTP_200_OK:
                return update_response

            # set modified_by
            maintenance_obj, modified_by_status = MaintenanceUpdater.update_maintenance_request_modified_by(maintenance_obj, user)
            if modified_by_status.status_code != status.HTTP_202_ACCEPTED:
                return maintenance_obj, modified_by_status

            # create asset event log
            description = "Maintenance " + str(maintenance_obj.work_order) + " status was set to " + new_status + "."
            event_log_response = MaintenanceHistory.create_maintenance_event_log(maintenance_obj, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            # -------------- Pusher -----------------
            event_name = None
            pusher_payload = {'location': maintenance_obj.location.location_id}
            # check if maintenance cancelled
            if maintenance_obj.status in [MaintenanceRequestModel.cancelled.lower(),MaintenanceRequestModel.denied.lower()]:
                event_name = PusherHelper.MaintenanceCancelledEvent
            # check if a maintenance that was originally complete is marked as incomplete
            elif original_status in MaintenanceRequestModel.complete_status_values and maintenance_obj.status not in MaintenanceRequestModel.complete_status_values:
                event_name = PusherHelper.MaintenanceIncompleteEvent
            # check if a maintenance that was originally incomplete is marked as complete
            elif original_status not in MaintenanceRequestModel.complete_status_values and maintenance_obj.status in MaintenanceRequestModel.complete_status_values:
                event_name = PusherHelper.MaintenanceCompleteEvent
            
            skip_push = False
            if new_status in MaintenanceRequestModel.complete_status_values and original_status in MaintenanceRequestModel.complete_status_values:
                skip_push = True
            if new_status not in MaintenanceRequestModel.complete_status_values and original_status not in MaintenanceRequestModel.complete_status_values:
                skip_push = True
            
            channel_name = DetailedUser.objects.get(email=user.email).company.company_name
            history_func = MaintenanceHistory.create_maintenance_record_by_obj
            pusher_helper = PusherHelper(channel_name, event_name, pusher_payload, skip_push, history_func)

            # create maintenance record
            if event_name is not None:
                if not pusher_helper.push(maintenance_obj):
                    Logger.getLogger().error(CustomError.MHF_2)
                    return maintenance_obj, Response(CustomError.get_full_error_json(CustomError.MHF_2), status=status.HTTP_400_BAD_REQUEST)
            
            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_list_maintenance(user):
        try:
            queryset = MaintenanceHelper.select_related_to_maintenance(MaintenanceRequestModel.objects.using(user.db_access).\
                filter(status__in=MaintenanceRequestModel.incomplete_status_values))
            relevant_qs = MaintenanceHelper.filter_maintenance_for_user(queryset, user)
            maintenance_id_list = relevant_qs.values_list('maintenance_id', flat=True)
            ser = LightMaintenanceRequestSerializer(relevant_qs, many=True,
            context=MaintenanceHelper.get_maintenance_ser_context(maintenance_id_list, user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_list_completed_maintenance(user):
        try:
            queryset = MaintenanceHelper.select_related_to_maintenance(MaintenanceRequestModel.objects.using(user.db_access).\
                filter(status__in=MaintenanceRequestModel.complete_status_values))
            relevant_qs = MaintenanceHelper.filter_maintenance_for_user(queryset, user)
            maintenance_id_list = relevant_qs.values_list('maintenance_id', flat=True)
            ser = LightMaintenanceRequestSerializer(relevant_qs, many=True,
            context=MaintenanceHelper.get_maintenance_ser_context(maintenance_id_list, user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_maintenance_by_vin(_vin, user):
        try:
            queryset = MaintenanceHelper.select_related_to_maintenance(MaintenanceRequestModel.objects.using(user.db_access).filter(VIN__VIN=_vin))
            relevant_qs = MaintenanceHelper.filter_maintenance_for_user(queryset, user)
            maintenance_id_list = relevant_qs.values_list('maintenance_id', flat=True)
            ser = LightMaintenanceRequestSerializer(relevant_qs, many=True,
            context=MaintenanceHelper.get_maintenance_ser_context(maintenance_id_list, user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_maintenance_details_by_id(maintenance_id, user):
        try:
            maintenance, maintenance_response = MaintenanceHelper.get_maintenance_request_by_id(maintenance_id, user.db_access)
            if maintenance_response.status_code != status.HTTP_302_FOUND:
                return maintenance_response
            ser = LightMaintenanceRequestSerializer(maintenance,
            context=MaintenanceHelper.get_maintenance_ser_context([maintenance.maintenance_id], user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_maintenance_details_by_work_order(work_order, user):
        try:
            maintenance, maintenance_response = MaintenanceHelper.get_maintenance_request_by_work_order(work_order, user.db_access)
            if maintenance_response.status_code != status.HTTP_302_FOUND:
                return maintenance_response
            ser = LightMaintenanceRequestSerializer(maintenance,
            context=MaintenanceHelper.get_maintenance_ser_context([maintenance.maintenance_id], user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_list_inspections(user):
        try:
            queryset = InspectionTypeHelper.get_all_inspection_types(user.db_access)
            ser = InspectionTypeSerializer(queryset, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_update_vendor_and_estimated_delivery_date(maintenance_id, request_data, user):
        try:
            maintenance = MaintenanceRequestModel.objects.using(user.db_access).get(maintenance_id=int(maintenance_id))
            if not AssetHelper.check_asset_status_active(maintenance.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)
            data = {}
            data['assigned_vendor'] = request_data.get('assigned_vendor')
            data['estimated_delivery_date'] = HelperMethods.date_string_to_datetime(request_data.get('estimated_delivery_date'))
            ser = MaintenanceRequestSerializer(maintenance, data, partial=True)

            if ser.is_valid():
                maintenance_obj = ser.save()

                # set modified_by
                maintenance_obj, modified_by_status = MaintenanceUpdater.update_maintenance_request_modified_by(maintenance_obj, user)
                if modified_by_status.status_code != status.HTTP_202_ACCEPTED:
                    return modified_by_status

                # create maintenance record
                if(not MaintenanceHistory.create_maintenance_record_by_obj(maintenance_obj)):
                    Logger.getLogger().error(CustomError.MHF_2)
                    return Response(CustomError.get_full_error_json(CustomError.MHF_2), status=status.HTTP_400_BAD_REQUEST)

                # create asset event log
                description = "Maintenance " + str(maintenance_obj.work_order) + " assigned vendor was set to " + str(maintenance_obj.assigned_vendor.vendor_name) + " and estimated delivery date was set to " + str(maintenance_obj.estimated_delivery_date) + "."
                event_log_response = MaintenanceHistory.create_maintenance_event_log(maintenance_obj, description)
                if event_log_response.status_code != status.HTTP_201_CREATED:
                    return event_log_response

                return Response(ser.data, status=status.HTTP_200_OK)

            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_incomplete_maintenance_request_count(user):
        try:
            qs = MaintenanceRequestModel.objects.using(user.db_access).exclude(status__in=[MaintenanceRequestModel.delivered,MaintenanceRequestModel.denied,MaintenanceRequestModel.cancelled])
            count = MaintenanceHelper.filter_maintenance_for_user(qs, user).count()
            return Response({"count":count}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_complete_maintenance_request_count(user):
        try:
            qs = MaintenanceRequestModel.objects.using(user.db_access).filter(status__in=[MaintenanceRequestModel.delivered,MaintenanceRequestModel.denied,MaintenanceRequestModel.cancelled])
            count = MaintenanceHelper.filter_maintenance_for_user(qs, user).count()
            return Response({"count":count}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_maintenance_request_percentage_complete(user):
        try:
            total_qs = MaintenanceRequestModel.objects.using(user.db_access).all()
            count_total =  MaintenanceHelper.filter_maintenance_for_user(total_qs, user).count()
            complete_qs = MaintenanceRequestModel.objects.filter(status=MaintenanceRequestModel.complete)
            count_complete =  MaintenanceHelper.filter_maintenance_for_user(complete_qs, user).count()
            percentageComplete = round((count_complete / count_total) * 100, 2)
            return Response({"completed_percent":percentageComplete}, status=status.HTTP_200_OK)
        except ZeroDivisionError as zde:
            Logger.getLogger().error(zde)
            return Response({"completed_percent":0}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_maintenance(request_data, user):
        try:
            # get maintenance
            maintenance_request, maintenance_request_response = MaintenanceHelper.get_maintenance_request_by_id(request_data.get("maintenance_id"), user.db_access)
            if maintenance_request_response.status_code != status.HTTP_302_FOUND:
                return maintenance_request_response

            if not AssetHelper.check_asset_status_active(getattr(maintenance_request, "VIN"), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            # update maintenance
            updated_maintenance_request, is_important, update_maintenance_request_response = MaintenanceUpdater.update_maintenance_fields(maintenance_request, request_data, user)
            if update_maintenance_request_response.status_code != status.HTTP_202_ACCEPTED:
                return update_maintenance_request_response
            # create maintenance record
            if(not MaintenanceHistory.create_maintenance_record_by_obj(updated_maintenance_request)):
                Logger.getLogger().error(CustomError.MHF_2)
                return Response(CustomError.get_full_error_json(CustomError.MHF_2), status=status.HTTP_400_BAD_REQUEST)
            # create asset event log
            description = "Maintenance " + str(updated_maintenance_request.work_order) + " was updated."
            event_log_response = MaintenanceHistory.create_maintenance_event_log(updated_maintenance_request, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            if is_important:
                # -------------- Email maintenance request(s) ---------------
                notification_config, resp = NotificationHelper.get_notification_config_by_name("New Maintenance", user.db_access)
                if resp.status_code != status.HTTP_302_FOUND:
                    return resp
                if notification_config.active and (
                    notification_config.triggers is None or (
                        "update_maintenance" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                    )
                ):
                    file_info, html_message = PdfManager.gen_maintenance_pdf_request([updated_maintenance_request], notification_config, user, is_update=True)
                    email_title = "Maintenance Request (ID " + str(maintenance_request.maintenance_id) + ") Has Been Updated - Auto-Generated Email"

                    if maintenance_request.in_house:
                        if notification_config.recipient_type == "auto":
                            recipients = UserHelper.get_managers_emails_by_location(user.db_access, [MaintenanceHelper.get_maintenance_location(updated_maintenance_request)])
                        else:
                            recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access)
                    else:
                        if notification_config.recipient_type == "auto":
                            managers = UserHelper.get_managers_emails_by_location(user.db_access, [MaintenanceHelper.get_maintenance_location(updated_maintenance_request)])
                            manager_list = [manager for manager in managers]
                            recipients = manager_list + [maintenance_request.vendor_email] 
                        else:
                            recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access) + [maintenance_request.vendor_email] 
                        
                    email_response = Email.send_email_notification(recipients, email_title, html_message, [], html_content=True)
                    if email_response.status_code != status.HTTP_200_OK:
                        return email_response
                # --------------------------------------------------
            
            updated_maintenance_request.save()

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
        
    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_supporting_files(maintenance_id, file_specs, request_files, user):
        try:
            file_entries = []
            
            for _file in request_files:
                
                file_purpose = None
                expiration_date = None
                file_info_arr = file_specs.get("file_info")
                
                for info in file_info_arr:
                    
                    if info.get("file_name") == _file.name:
                        file_purpose = info.get("purpose").lower()                       
                        expiration_date = info.get("expiration_date")                        
                        if not MaintenanceHelper.validate_purpose(file_purpose):
                            return Response(CustomError.get_full_error_json(CustomError.FUF_2), status=status.HTTP_400_BAD_REQUEST)
                

                # ------------ Upload files to blob --------------
                company_name = UserHelper.get_company_name_by_user_email(user.email, user.db_access)
                maintenance_obj = MaintenanceRequestModel.objects.using(user.db_access).get(maintenance_id=maintenance_id)

                if not AssetHelper.check_asset_status_active(maintenance_obj.VIN, user.db_access):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                       CustomError.get_error_user(CustomError.TUF_16)))
                    return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                    CustomError.get_error_user(CustomError.TUF_16)),
                                    status=status.HTTP_400_BAD_REQUEST)
                
                file_prefix = str(file_purpose.replace(" ", "_")) + "_" + str(maintenance_obj.maintenance_id) + "_"
                container = "maintenance"
                file_status, file_info = BlobStorageHelper.write_file_to_blob(_file, container, file_prefix, company_name, user.db_access)
                if(not file_status):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_0))
                    return Response(CustomError.get_full_error_json(CustomError.FUF_0), status=status.HTTP_400_BAD_REQUEST)

                # ------------ Create file entry -----------------
                detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
                file_entry = MaintenanceUpdater.construct_maintenance_file_instance(maintenance_obj, file_info, file_purpose, expiration_date, detailed_user)

                file_entries.append(file_entry)

            # Upload file entries to db
            MaintenanceRequestFile.objects.using(user.db_access).bulk_create(file_entries)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)
