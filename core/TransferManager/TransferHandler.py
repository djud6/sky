from api.Models.transfer_file import TransferFile
from core.HistoryManager.AssetHistory import AssetHistory
from api.Models.asset_model import AssetModel
from api.Models.RolePermissions import RolePermissions
from core.AssetManager.AssetUpdater import AssetUpdater
from rest_framework.response import Response
from rest_framework import status
from ..Helper import HelperMethods
from ..ApprovalManager.ApprovalHandler import ApprovalHandler
from ..AssetManager.AssetHelper import AssetHelper
from ..FileManager.FileHelper import FileHelper
from ..BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from ..DisposalManager.DisposalHelper import DisposalHelper
from ..UserManager.UserHelper import UserHelper
from ..NotificationManager.NotificationHelper import NotificationHelper
from .TransferUpdater import TransferUpdater
from .TransferHelper import TransferHelper
from ..HistoryManager.TransferHistory import TransferHistory
from api.Models.asset_transfer import AssetTransfer
from api.Serializers.serializers import AssetTransferSerializer
from GSE_Backend.errors.ErrorDictionary import CustomError
from ..FileManager.PdfManager import PdfManager
from communication.EmailService.EmailService import Email

import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class TransferHandler():

    @staticmethod
    def handle_add_transfer(request, user):

        try:
            data = HelperMethods.json_str_to_dict(request.POST['data'])
            file_specs = HelperMethods.json_str_to_dict(request.POST['file_specs'])
            files = request.FILES.getlist('files')

            transfer_data = data.get("transfer_data")
            approval_data = {
                "title": "Transfer Request",
                "description": transfer_data.get("justification"),
                "VIN": transfer_data.get("VIN")
            }
            # Check status of VIN --> Could be inoperative
            if not AssetHelper.check_asset_status_active(transfer_data.get('VIN'), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            # Check to see if disposal object exists if this asset transfer is created from disposal
            if transfer_data.get("disposal") is not None:
                if not DisposalHelper.asset_disposal_entry_exists(user.db_access, transfer_data.get("disposal")):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.DDNE_0))
                    return Response(CustomError.get_full_error_json(CustomError.DDNE_0),
                                    status=status.HTTP_400_BAD_REQUEST)

            # Create transfer request
            sender_detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            transfer_request, create_transfer_response = TransferUpdater.create_transfer_request(transfer_data,
                                                                                                 user,
                                                                                                 sender_detailed_user)
            if create_transfer_response.status_code != status.HTTP_201_CREATED:
                return create_transfer_response

            # Update fields after db entry has been made
            transfer_request, update_status = TransferUpdater.update_transfer_post_creation(transfer_request,
                                                                                            sender_detailed_user)
            if update_status.status_code != status.HTTP_202_ACCEPTED:
                return update_status

            try:
                # ------------ Check files types -----------------
                valid_transfer_file_types = ["application/pdf"]
                if not FileHelper.verify_files_are_accepted_types(files, valid_transfer_file_types):
                    AssetTransfer.objects.filter(asset_transfer_id=transfer_request.asset_transfer_id).delete()
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_1, "File(s) not pdf."))
                    return Response(CustomError.get_full_error_json(CustomError.FUF_1,
                                                                    "File(s) not pdf."),
                                    status=status.HTTP_400_BAD_REQUEST)

                # ------------ Upload files to blob --------------
                file_response = TransferHandler.handle_add_supporting_files(transfer_request, file_specs, files, user)
                if(file_response.status_code != status.HTTP_200_OK):
                    AssetTransfer.objects.filter(asset_transfer_id=transfer_request.asset_transfer_id).delete()
                    return file_response

                # -------------- Email asset transfer report ---------------
                notification_config, resp = NotificationHelper.get_notification_config_by_name("New Transfer",
                                                                                               user.db_access)
                if resp.status_code != status.HTTP_302_FOUND:
                    return resp
                if notification_config.active and (
                    notification_config.triggers is None or (
                        "add_transfer" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                    )
                ):
                    fileInfo, htmlMessage = PdfManager.gen_transfer_pdf_report(transfer_request,
                                                                               notification_config, user)
                    email_title = (f"New Asset Transfer Request (ID {str(transfer_request.asset_transfer_id)}"
                                   f") - Auto-Generated Email")

                    if notification_config.recipient_type == "auto":
                        recipients = TransferHelper.get_executives_emails(user.db_access)
                    else:
                        recipients = NotificationHelper.get_recipients_for_notification(notification_config,
                                                                                        user.db_access)

                    if(fileInfo is not None):
                        email_response = Email.send_email_notification(recipients,
                                                                       email_title, htmlMessage, [fileInfo],
                                                                       html_content=True)
                    else:
                        email_response = Email.send_email_notification(recipients, email_title, htmlMessage,
                                                                       [], html_content=True)
            
                    if email_response.status_code != status.HTTP_200_OK:
                        AssetTransfer.objects.filter(asset_transfer_id=transfer_request.asset_transfer_id).delete()
                        return email_response
            # -------------------------------------------------
            except Exception as e:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
                return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

            # update the asset last process
            AssetUpdater.update_last_process(transfer_data.get("VIN"), AssetModel.Transfer)

            # create asset history record
            if not AssetHistory.create_asset_record(transfer_data.get("VIN"), user.db_access):
                Logger.getLogger().error(CustomError.MHF_0)
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            # Create transfer history record
            if not TransferHistory.create_transfer_record_by_obj(transfer_request):
                Logger.getLogger().error(CustomError.MHF_9)
                return Response(CustomError.get_full_error_json(CustomError.MHF_9), status=status.HTTP_400_BAD_REQUEST)

            # create asset event log
            description = "Asset transfer request " + str(transfer_request.custom_id) + " was created."
            event_log_response = TransferHistory.create_asset_transfer_event_log(transfer_request, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response
            approval_data['asset_transfer_request'] = str(transfer_request.asset_transfer_id)

            # Create an approval request
            create_approvals_response = ApprovalHandler.handle_create_approval_request(approval_data, user)
            if create_approvals_response.status_code != status.HTTP_201_CREATED:
                return create_approvals_response

            return Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            Logger.getLogger().error(CustomError.G_0, e)
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_transfer_cancelled(asset_obj, user):
        try:
            # Update asset last process
            prev_last_process = AssetHelper.get_previous_different_last_process(asset_obj, user.db_access)
            asset_obj = AssetUpdater.update_last_process(asset_obj.VIN, prev_last_process)

            # Create asset history record
            if(not AssetHistory.create_asset_record_by_obj(asset_obj)):
                Logger.getLogger().error(CustomError.MHF_0)
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            return asset_obj, Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.G_0, e)
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_transfer_in_transit(transfer_obj, asset_obj, data, user):
        try:
            # Check if interior/exterior condition is valid
            if (not TransferHelper.is_condition_valid(data.get('interior_condition')) or
            not TransferHelper.is_condition_valid(data.get('exterior_condition'))):
                Logger.getLogger().error(CustomError.IAT_3)
                return transfer_obj, asset_obj, Response(CustomError.get_full_error_json(CustomError.IAT_3), status=status.HTTP_400_BAD_REQUEST)
                
            # Check if interior/exterior details are present
            if ((len(str(data.get("interior_condition_details"))) == 0 or data.get("interior_condition_details") is None) or
            (len(str(data.get("exterior_condition_details"))) == 0 or data.get("exterior_condition_details") is None)):
                Logger.getLogger().error(CustomError.IAT_4)
                return transfer_obj, asset_obj, Response(CustomError.get_full_error_json(CustomError.IAT_4), status=status.HTTP_400_BAD_REQUEST)

            # Check if correct usage fields were provided
            if not AssetHelper.usage_parameters_provided(asset_obj, data):
                Logger.getLogger().error(CustomError.IAT_5)
                return transfer_obj, asset_obj, Response(CustomError.get_full_error_json(CustomError.IAT_5), status=status.HTTP_400_BAD_REQUEST)

            # Update condition and usage fields
            transfer_obj, is_important, update_response = TransferUpdater.update_transfer(transfer_obj, data, user)
            if update_response.status_code != status.HTTP_202_ACCEPTED:
                return transfer_obj, asset_obj, update_response
            transfer_obj.save()

            # Update asset usage
            asset_obj, update_response = AssetUpdater.update_usage(asset_obj.VIN, mileage=data.get('mileage'), hours=data.get('hours'), db_name=user.db_access)
            if update_response.status_code != status.HTTP_200_OK:
                return transfer_obj, asset_obj, update_response

            # create asset record 
            if not AssetHistory.create_asset_record_by_obj(asset_obj):
                Logger.getLogger().error(CustomError.MHF_0)
                return transfer_obj, asset_obj, Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            return transfer_obj, asset_obj, Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.G_0, e)
            return transfer_obj, asset_obj, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_update_transfer_status(data, file_specs, files, user):
        try:
            _transfer_id = data.get('transfer_id')
            _status = data.get('status')

            # Check if the user is a manager, if not return an unauthorized error
            if UserHelper.get_role_by_email(user.email, user.db_access) not in (RolePermissions.manager, RolePermissions.executive):
                Logger.getLogger().error(CustomError.NATPA_0)
                return Response(CustomError.get_full_error_json(CustomError.NATPA_0), status=status.HTTP_401_UNAUTHORIZED)

            # Check if status is valid
            if not TransferHelper.is_status_valid(_status):
                Logger.getLogger().error(CustomError.IAT_1)
                return Response(CustomError.get_full_error_json(CustomError.IAT_1), status=status.HTTP_400_BAD_REQUEST)

            transfer_obj, transfer_request_response = TransferHelper.get_transfer_by_id(_transfer_id, user.db_access)
            if transfer_request_response.status_code != status.HTTP_302_FOUND:
                return transfer_request_response

            # Check status of VIN --> Could be inoperative
            if not AssetHelper.check_asset_status_active(transfer_obj.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            asset_obj = AssetHelper.get_asset_by_VIN(transfer_obj.VIN, user.db_access)

            # Is status new
            if not TransferHelper.is_status_new(transfer_obj, _status):
                Logger.getLogger().error(CustomError.IAT_2)
                return Response(CustomError.get_full_error_json(CustomError.IAT_2), status=status.HTTP_400_BAD_REQUEST)

            # Status specific actions
            # NOTE: In the future if certain files are required for a particular status to be set, the checks for
            # said files can be done inside the status specific handlers.
            if str(_status).lower() == AssetTransfer.cancelled:
                asset_obj, actions_response = TransferHandler.handle_transfer_cancelled(asset_obj, user)
            elif str(_status).lower() == AssetTransfer.in_transit:
                transfer_obj, asset_obj, actions_response = TransferHandler.handle_transfer_in_transit(transfer_obj, asset_obj, data, user)
            else:
                actions_response = Response(status=status.HTTP_202_ACCEPTED)

            if actions_response.status_code != status.HTTP_202_ACCEPTED:
                return actions_response

            # Upload files
            file_upload_response = TransferHandler.handle_add_supporting_files(transfer_obj, file_specs, files, user)
            if file_upload_response.status_code != status.HTTP_200_OK:
                return file_upload_response

            # Update transfer status
            transfer_obj, asset_obj, update_response = TransferUpdater.update_transfer_status(transfer_obj, asset_obj, _status, user)
            if update_response.status_code != status.HTTP_202_ACCEPTED:
                return transfer_obj, update_response

            # Create transfer history record
            if(not TransferHistory.create_transfer_record_by_obj(transfer_obj)):
                Logger.getLogger().error(CustomError.MHF_9)
                return Response(CustomError.get_full_error_json(CustomError.MHF_9), status=status.HTTP_400_BAD_REQUEST)

            # Create asset log entry
            description = "Asset transfer request " + str(transfer_obj.custom_id) + " status was set to " + str(_status) + "."
            event_log_response = TransferHistory.create_asset_transfer_event_log(transfer_obj, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.G_0, e)
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)    

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_transfers_for_user_location(request):
        try:
            user_related_transfers, search_response = TransferHelper.get_user_location_related_transfers(request.user)
            if search_response.status_code != status.HTTP_302_FOUND:
                return search_response

            user_related_transfers = TransferHelper.select_related_to_transfer(user_related_transfers)
            transfer_id_list = user_related_transfers.values_list('asset_transfer_id', flat=True)
            serialized_response = AssetTransferSerializer(user_related_transfers, many=True,
            context=TransferHelper.get_transfer_ser_context(transfer_id_list, request.user.db_access))
            return Response(serialized_response.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.G_0, e)
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_transfers_for_user_location_by_vin(request, _vin):
        try:
            user_related_transfers, search_response = TransferHelper.get_user_location_related_transfers_by_vin(request.user, _vin)
            if search_response.status_code != status.HTTP_200_OK:
                return search_response

            user_related_transfers = TransferHelper.select_related_to_transfer(user_related_transfers)
            transfer_id_list = user_related_transfers.values_list('asset_transfer_id', flat=True)
            serialized_response = AssetTransferSerializer(user_related_transfers, many=True,
            context=TransferHelper.get_transfer_ser_context(transfer_id_list, request.user.db_access))
            return Response(serialized_response.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.G_0, e)
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
    
# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod 
    def handle_get_asset_transfer_list(user):
        try:
            all_transfers = TransferHelper.get_asset_transfers(user.db_access)
            all_transfers = TransferHelper.select_related_to_transfer(all_transfers)
            transfer_id_list = all_transfers.values_list('asset_transfer_id', flat=True)
            serialized_response = AssetTransferSerializer(all_transfers, many=True,
            context=TransferHelper.get_transfer_ser_context(transfer_id_list, user.db_access))
            return Response(serialized_response.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.G_0, e)
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod 
    def handle_get_asset_transfer_by_id(transfer_id, user):
        try:
            transfer, transfer_response = TransferHelper.get_transfer_by_id(transfer_id, user.db_access)
            if transfer_response.status_code != status.HTTP_302_FOUND:
                return transfer_response

            serialized_response = AssetTransferSerializer(transfer,
            context=TransferHelper.get_transfer_ser_context([transfer.asset_transfer_id], user.db_access))
            return Response(serialized_response.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.G_0, e)
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod 
    def handle_get_asset_transfer_by_custom_id(custom_transfer_id, user):
        try:
            transfer, transfer_response = TransferHelper.get_transfer_by_custom_id(custom_transfer_id, user.db_access)
            if transfer_response.status_code != status.HTTP_302_FOUND:
                return transfer_response
                
            serialized_response = AssetTransferSerializer(transfer,
            context=TransferHelper.get_transfer_ser_context([transfer.asset_transfer_id], user.db_access))
            return Response(serialized_response.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.G_0, e)
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_transfer(request_data, user):
        try:
            # get transfer
            transfer, transfer_response = TransferHelper.get_transfer_by_id(request_data.get('transfer_id'), user.db_access)
            if transfer_response.status_code != status.HTTP_302_FOUND:
                return transfer_response

            # Check status of VIN --> Could be inoperative
            if not AssetHelper.check_asset_status_active(transfer.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            # update transfer
            updated_transfer, is_important, update_transfer_response = TransferUpdater.update_transfer(transfer, request_data, user)
            if update_transfer_response.status_code != status.HTTP_202_ACCEPTED:
                return update_transfer_response

            # Create transfer history record
            if(not TransferHistory.create_transfer_record_by_obj(updated_transfer)):
                Logger.getLogger().error(CustomError.MHF_9)
                return Response(CustomError.get_full_error_json(CustomError.MHF_9), status=status.HTTP_400_BAD_REQUEST)

            # create asset event log
            description = "Asset transfer request " + str(updated_transfer.custom_id) + " was updated."
            event_log_response = TransferHistory.create_asset_transfer_event_log(updated_transfer, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            if is_important:
                # -------------- Email asset transfer report ---------------
                notification_config, resp = NotificationHelper.get_notification_config_by_name("New Transfer", user.db_access)
                if resp.status_code != status.HTTP_302_FOUND:
                    return resp
                if notification_config.active and (
                    notification_config.triggers is None or (
                        "update_transfer" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                    )
                ):
                    fileInfo, htmlMessage = PdfManager.gen_transfer_pdf_report(updated_transfer, notification_config, user, is_update=True)
                    email_title = "Transfer Request (ID " + str(updated_transfer.asset_transfer_id) + ") " + " Has Been Updated - Auto-Generated Email"

                    if notification_config.recipient_type == "auto":
                        recipients = UserHelper.get_managers_emails_by_location(user.db_access, [transfer.original_location.location_id, transfer.destination_location.location_id])
                    else:
                        recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access)

                    if(fileInfo is not None):
                        email_response = Email.send_email_notification(recipients, email_title, htmlMessage, [fileInfo], html_content=True)
                    else:
                        email_response = Email.send_email_notification(recipients, email_title, htmlMessage, [], html_content=True)
                    if email_response.status_code != status.HTTP_200_OK:
                        return email_response
                # -------------------------------------------------

            updated_transfer.save()

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.G_0, e)
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
        
# ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_supporting_files(transfer_obj, file_specs, request_files, user):
        try:
            file_entries = []
            for _file in request_files:
                file_purpose = None
                for info in file_specs.get("file_info"):
                    if info.get("file_name") == _file.name:
                        file_purpose = info.get("purpose").lower()
                        break
                if not TransferHelper.validate_purpose(file_purpose):
                    return Response(CustomError.get_full_error_json(CustomError.FUF_2), status=status.HTTP_400_BAD_REQUEST)

                # ------------ Upload files to blob --------------
                company_name = UserHelper.get_company_name_by_user_email(user.email, user.db_access)
                file_prefix = str(file_purpose.replace(" ", "_")) + "_" + str(transfer_obj.asset_transfer_id) + "_"
                container = "transfer"
                file_status, file_info = BlobStorageHelper.write_file_to_blob(_file, container, file_prefix, company_name, user.db_access)
                if(not file_status):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_0))
                    return Response(CustomError.get_full_error_json(CustomError.FUF_0), status=status.HTTP_400_BAD_REQUEST)

                # ------------ Create file entry -----------------
                detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
                file_entry = TransferUpdater.construct_transfer_file_instance(transfer_obj, file_info, file_purpose, detailed_user)

                file_entries.append(file_entry)

            # Upload file entries to db
            TransferFile.objects.using(user.db_access).bulk_create(file_entries)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)