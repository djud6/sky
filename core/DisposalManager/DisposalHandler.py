from core.AccidentManager.AccidentHelper import AccidentHelper
from core.AssetManager.AssetHelper import AssetHelper
from api.Models.repairs import RepairsModel
from core.RepairManager.RepairHelper import RepairHelper
from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_model import AssetModel
from api.Models.asset_log import AssetLog
from api.Models.asset_disposal import AssetDisposalModel
from api.Models.asset_disposal_file import AssetDisposalFile
from ..CompanyManager.CompanyHelper import CompanyHelper
from .DisposalHelper import DisposalHelper
from .DisposalUpdater import DisposalUpdater
from ..AssetManager.AssetUpdater import AssetUpdater
from ..AssetManager.AssetHandler import AssetHandler
from ..UserManager.UserHelper import UserHelper
from ..NotificationManager.NotificationHelper import NotificationHelper
from ..Helper import HelperMethods
from ..BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from ..FileManager.PdfManager import PdfManager
from ..UserManager.UserHelper import UserHelper
from communication.EmailService.EmailService import Email
from api.Serializers.serializers import LightAssetDisposalSerializer, AssetDisposalSerializer
from ..HistoryManager.DisposalHistory import DisposalHistory
from ..HistoryManager.AssetHistory import AssetHistory
from GSE_Backend.errors.ErrorDictionary import CustomError
from core.AssetRequestManager.AssetRequestHelper import AssetRequestHelper
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class DisposalHandler():

    # ----------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_company_directed_sale(request_data, file_specs, files, user):

        if not AssetHelper.check_asset_status_active(request_data["VIN"], user.db_access):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                               CustomError.get_error_user(CustomError.TUF_16)))
            return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                            CustomError.get_error_user(CustomError.TUF_16)),
                            status=status.HTTP_400_BAD_REQUEST)


        if request_data["disposal_type"].lower() == "company directed sale":
            # creates the asset disposal
            disposal_obj, add_disposal_status = DisposalHandler.handle_add_asset_disposal(request_data, file_specs, files, user)

            if add_disposal_status.status_code != status.HTTP_201_CREATED:
                return add_disposal_status

            # Update asset status
            AssetUpdater.update_asset_status(disposal_obj.VIN, AssetModel.Inop)
            
            return Response(data={"disposal_id": disposal_obj.id}, status=status.HTTP_201_CREATED)

        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.RAD_2))
            return Response(CustomError.get_full_error_json(CustomError.RAD_2), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_auction_disposal(request_data, file_specs, files, user):

        if not AssetHelper.check_asset_status_active(request_data["VIN"], user.db_access):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                               CustomError.get_error_user(CustomError.TUF_16)))
            return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                            CustomError.get_error_user(CustomError.TUF_16)),
                            status=status.HTTP_400_BAD_REQUEST)

        if request_data["disposal_type"].lower() == "auction":
            # creates the asset disposal
            disposal_obj, add_disposal_status = DisposalHandler.handle_add_asset_disposal(request_data, file_specs, files, user)

            if add_disposal_status.status_code != status.HTTP_201_CREATED:
                return add_disposal_status

            # Update asset status
            AssetUpdater.update_asset_status(disposal_obj.VIN, AssetModel.Inop)

            company_obj = CompanyHelper.get_list_companies(user.db_access)[0]

            # send the email
            # ----------------- Email Manager and Vendor -------------------
            notification_config, resp = NotificationHelper.get_notification_config_by_name("New Auction Disposal", user.db_access)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp
            if notification_config.active and (
                    notification_config.triggers is None or (
                        "add_auction" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                )
            ):
                htmlMessage = PdfManager.gen_auction_disposal_report(disposal_obj, company_obj, notification_config, user)
                email_title = "New Auction Disposal (ID " + str(disposal_obj.id) + ") - Auto-Generated email"

                vendor_email = disposal_obj.vendor_email
                if notification_config.recipient_type == "auto":
                    recipients = [vendor_email]
                else:
                    recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access) + [vendor_email]
                
                # get the files that have to be attached in the email sent to the vendor
                disposal_files = DisposalHelper.get_files_for_disposal(files, user.db_access, disposal_obj.VIN)
                email_response = Email.send_email_notification(recipients, email_title, htmlMessage, disposal_files, html_content=True)
                if email_response.status_code != status.HTTP_200_OK:
                    DisposalUpdater.delete_failed_disposal_requests([disposal_obj], user.db_access)
                    return email_response

                # update vendor contacted date
                disposal_obj = DisposalUpdater.update_vendor_contacted_date(disposal_obj)
                disposal_obj.save()

            return Response(data={"disposal_id": disposal_obj.id}, status=status.HTTP_201_CREATED)
        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.RAD_2))
            return Response(CustomError.get_full_error_json(CustomError.RAD_2), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_repurpose_disposal(request_data, file_specs, files, user):

        if not AssetHelper.check_asset_status_active(request_data["VIN"], user.db_access):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                               CustomError.get_error_user(CustomError.TUF_16)))
            return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                            CustomError.get_error_user(CustomError.TUF_16)),
                            status=status.HTTP_400_BAD_REQUEST)

        if request_data["disposal_type"].lower() == "repurpose":
            disposal_obj, add_disposal_status = DisposalHandler.handle_add_asset_disposal(request_data, file_specs, files, user)

            if add_disposal_status.status_code != status.HTTP_201_CREATED:
                return add_disposal_status

            # Update asset status
            AssetUpdater.update_asset_status(disposal_obj.VIN, AssetModel.Inop)
            
            return Response(data={"disposal_id": disposal_obj.id}, status=status.HTTP_201_CREATED)
        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.RAD_2))
            return Response(CustomError.get_full_error_json(CustomError.RAD_2), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_scrap_disposal(request_data, file_specs, files, user):

        if not AssetHelper.check_asset_status_active(request_data["VIN"], user.db_access):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                               CustomError.get_error_user(CustomError.TUF_16)))
            return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                            CustomError.get_error_user(CustomError.TUF_16)),
                            status=status.HTTP_400_BAD_REQUEST)

        if request_data["disposal_type"].lower() == "scrap":
            #checks if request_data contains will_strip
            if not DisposalHelper.check_valid_scrap(request_data):
                Logger.getLogger().error(CustomError.RAD_1)
                return Response(CustomError.get_full_error_json(CustomError.RAD_1), status=status.HTTP_400_BAD_REQUEST)
            
            # add the asset disposal
            disposal_obj, add_disposal_status = DisposalHandler.handle_add_asset_disposal(request_data, file_specs, files, user)

            if add_disposal_status.status_code != status.HTTP_201_CREATED:
                return add_disposal_status

            # Update asset status
            AssetUpdater.update_asset_status(disposal_obj.VIN, AssetModel.Inop)
            
            company_obj = CompanyHelper.get_list_companies(user.db_access)[0]
            # ----------------- Email Manager and Vendor -------------------
            notification_config, resp = NotificationHelper.get_notification_config_by_name("New Scrap Disposal", user.db_access)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp
            if notification_config.active and (
                    notification_config.triggers is None or (
                        "add_scrap" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                )
            ):
                htmlMessage = PdfManager.gen_scrap_disposal_report(disposal_obj, company_obj, notification_config, user)
                email_title = "New Scrap Disposal (ID " + str(disposal_obj.id) + ") - Auto-Generated email"

                vendor_email = disposal_obj.vendor_email
                if notification_config.recipient_type == "auto":
                    recipients = [vendor_email]
                else:
                    recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access) + [vendor_email]

                # get the files that have to be attached in the email sent to the vendor
                disposal_files = DisposalHelper.get_files_for_disposal(files, user.db_access, disposal_obj.VIN)
                email_response = Email.send_email_notification(recipients, email_title, htmlMessage, disposal_files, html_content=True)

                if email_response.status_code != status.HTTP_200_OK:
                    DisposalUpdater.delete_failed_disposal_requests([disposal_obj], user.db_access)
                    return email_response

                # update vendor contacted date
                disposal_obj = DisposalUpdater.update_vendor_contacted_date(disposal_obj)
                disposal_obj.save()

            return Response(data={"disposal_id": disposal_obj.id}, status=status.HTTP_201_CREATED)
        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.RAD_2))
            return Response(CustomError.get_full_error_json(CustomError.RAD_2), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_donation_disposal(request_data, file_specs, files, user):

        if not AssetHelper.check_asset_status_active(request_data["VIN"], user.db_access):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                               CustomError.get_error_user(CustomError.TUF_16)))
            return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                            CustomError.get_error_user(CustomError.TUF_16)),
                            status=status.HTTP_400_BAD_REQUEST)

        if request_data["disposal_type"].lower() == "donate":
            # add the asset disposal
            disposal_obj, add_disposal_status = DisposalHandler.handle_add_asset_disposal(request_data, file_specs, files, user)

            if add_disposal_status.status_code != status.HTTP_201_CREATED:
                return add_disposal_status

            # Update asset status
            AssetUpdater.update_asset_status(disposal_obj.VIN, AssetModel.Inop)

            company_obj = CompanyHelper.get_list_companies(user.db_access)[0]
            # ----------------- Email Manager and Vendor -------------------
            notification_config, resp = NotificationHelper.get_notification_config_by_name("New Donation Disposal", user.db_access)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp
            if notification_config.active and (
                    notification_config.triggers is None or (
                        "add_donation" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                )
            ):
                htmlMessage = PdfManager.gen_donate_disposal_report(disposal_obj, company_obj, notification_config, user)
                email_title = "New Donation Disposal (ID " + str(disposal_obj.id) + ") - Auto-Generated email"

                vendor_email = disposal_obj.vendor_email
                if notification_config.recipient_type == "auto":
                    recipients = [vendor_email]
                else:
                    recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access) + [vendor_email]
                
                # get the files that have to be attached in the email sent to the vendor
                disposal_files = DisposalHelper.get_files_for_disposal(files, user.db_access, disposal_obj.VIN)
                email_response = Email.send_email_notification(recipients, email_title, htmlMessage, disposal_files, html_content=True)
                if email_response.status_code != status.HTTP_200_OK:
                    DisposalUpdater.delete_failed_disposal_requests([disposal_obj], user.db_access)
                    return email_response

                # update vendor contacted date
                disposal_obj = DisposalUpdater.update_vendor_contacted_date(disposal_obj)
                disposal_obj.save()

            return Response(data={"disposal_id": disposal_obj.id}, status=status.HTTP_201_CREATED)
        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.RAD_2))
            return Response(CustomError.get_full_error_json(CustomError.RAD_2), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_tradein_disposal(request_data, file_specs, files, user):

        if not AssetHelper.check_asset_status_active(request_data["VIN"], user.db_access):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                               CustomError.get_error_user(CustomError.TUF_16)))
            return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                            CustomError.get_error_user(CustomError.TUF_16)),
                            status=status.HTTP_400_BAD_REQUEST)

        if request_data["disposal_type"].lower() == "trade in":
            # add the asset disposal
            disposal_obj, add_disposal_status = DisposalHandler.handle_add_asset_disposal(request_data, file_specs, files, user)
            
            if add_disposal_status.status_code != status.HTTP_201_CREATED:
                return add_disposal_status

            # Update asset status
            AssetUpdater.update_asset_status(disposal_obj.VIN, AssetModel.Inop)
            
            return Response(data={"disposal_id": disposal_obj.id}, status=status.HTTP_201_CREATED)
        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.RAD_2))
            return Response(CustomError.get_full_error_json(CustomError.RAD_2), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_transfer_disposal(request_data, file_specs, files, user):

        if not AssetHelper.check_asset_status_active(request_data["VIN"], user.db_access):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                               CustomError.get_error_user(CustomError.TUF_16)))
            return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                            CustomError.get_error_user(CustomError.TUF_16)),
                            status=status.HTTP_400_BAD_REQUEST)

        if request_data["disposal_type"].lower() == "transfer":
            disposal_obj, add_disposal_status = DisposalHandler.handle_add_asset_disposal(request_data, file_specs, files, user)

            if add_disposal_status.status_code != status.HTTP_201_CREATED:
                return add_disposal_status
            
            return Response(data={"disposal_id": disposal_obj.id}, status=status.HTTP_201_CREATED)
        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.RAD_2))
            return Response(CustomError.get_full_error_json(CustomError.RAD_2), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_writeoff_disposal(request_data, file_specs, files, user):

        if not AssetHelper.check_asset_status_active(request_data["VIN"], user.db_access):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                               CustomError.get_error_user(CustomError.TUF_16)))
            return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                            CustomError.get_error_user(CustomError.TUF_16)),
                            status=status.HTTP_400_BAD_REQUEST)

        if request_data["disposal_type"].lower() == "write-off":
            disposal_obj, add_disposal_status = DisposalHandler.handle_add_asset_disposal(request_data, file_specs, files, user)

            if add_disposal_status.status_code != status.HTTP_201_CREATED:
                return add_disposal_status

            # Update asset status
            AssetUpdater.update_asset_status(disposal_obj.VIN, AssetModel.Inop)
            
            return Response(data={"disposal_id": disposal_obj.id}, status=status.HTTP_201_CREATED)
        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.RAD_2))
            return Response(CustomError.get_full_error_json(CustomError.RAD_2), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_asset_disposal(request_data, file_specs, files, user):
        try:

            if not AssetHelper.check_asset_status_active(request_data["VIN"], user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            ser = AssetDisposalSerializer(data=DisposalHelper.update_disposal_dict(request_data, user.db_access))
            if(ser.is_valid()):
                if AssetDisposalModel.objects.filter(VIN=ser.validated_data.get("VIN"), status="complete").exists():
                    Logger.getLogger().error(CustomError.ADE_0)
                    return None, Response(CustomError.get_full_error_json(CustomError.ADE_0), status=status.HTTP_400_BAD_REQUEST)

                if AssetDisposalModel.objects.filter(VIN=ser.validated_data.get("VIN"), status="incomplete").exists():
                    Logger.getLogger().error(CustomError.ADE_1)
                    return None, Response(CustomError.get_full_error_json(CustomError.ADE_1), status=status.HTTP_400_BAD_REQUEST)

                # add the files
                file_upload_response = AssetHandler.handle_add_supporting_files(ser.validated_data.get("VIN"), file_specs, files, user)
                if file_upload_response.status_code != status.HTTP_200_OK:
                    return None, file_upload_response

                disposal_request_obj = ser.save()

                # update fields after db entry has been made
                disposal_request_obj, update_status = DisposalUpdater.update_disposal_request_post_creation(disposal_request_obj, user)
                if update_status.status_code != status.HTTP_202_ACCEPTED:
                    return None, update_status

                # create disposal record 
                if not DisposalHistory.create_asset_disposal_record_by_obj(disposal_request_obj, user.db_access):
                    Logger.getLogger().error(DisposalHelper.get_disposal_history_error(disposal_request_obj.disposal_type))
                    return None, Response(CustomError.get_full_error_json(DisposalHelper.get_disposal_history_error(disposal_request_obj.disposal_type)), 
                                          status=status.HTTP_400_BAD_REQUEST)

                # create disposal event log
                description = "Disposal request (" + str(disposal_request_obj.disposal_type) + ") " + str(disposal_request_obj.custom_id) + " was created."
                event_log_response = DisposalHistory.create_asset_disposal_event_log(disposal_request_obj, description)
                if event_log_response.status_code != status.HTTP_201_CREATED:
                    return None, event_log_response

                # update asset last process
                AssetUpdater.update_last_process(ser.validated_data.get("VIN"), AssetModel.Disposal)

                # create asset record 
                if(not AssetHistory.create_asset_record(ser.validated_data.get("VIN"), user.db_access)):
                    Logger.getLogger().error(CustomError.MHF_0)
                    return None, Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

                return disposal_request_obj, Response(data={"disposal_id": disposal_request_obj.id}, status=status.HTTP_201_CREATED)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return None, Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return None, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_asset_disposals(user):
        try:
            disposals = DisposalHelper.select_related_to_disposal(DisposalHelper.get_asset_disposals(user.db_access))
            relevant_disposals = DisposalHelper.filter_disposal_for_user(disposals, user)
            disposal_id_list = relevant_disposals.values_list('id', flat=True)
            ser = LightAssetDisposalSerializer(relevant_disposals, many=True,
            context=DisposalHelper.get_disposal_ser_context(disposal_id_list, user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_asset_disposals_write_off_no_accident(user):
        try:
            accidents_with_disposal_ids= list(AccidentHelper.get_all_ids_with_disposals(user.db_access))
            write_offs = DisposalHelper.get_write_offs(user.db_access)
            without_accidents = write_offs.exclude(id__in = accidents_with_disposal_ids)
            disposals = DisposalHelper.select_related_to_disposal(without_accidents)
            relevant_disposals = DisposalHelper.filter_disposal_for_user(disposals, user)
            disposal_id_list = relevant_disposals.values_list('id', flat=True)
            ser = LightAssetDisposalSerializer(relevant_disposals, many=True,
            context=DisposalHelper.get_disposal_ser_context(disposal_id_list, user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_asset_disposal_details_by_id(disposal_id, user):
        try:
            disposal, disposal_response = DisposalHelper.get_disposal_request_by_id(disposal_id, user.db_access)
            if disposal_response.status_code != status.HTTP_302_FOUND:
                return disposal_response
            ser = LightAssetDisposalSerializer(disposal, context=DisposalHelper.get_disposal_ser_context([disposal.id], user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_asset_disposal_details_by_custom_id(custom_disposal_id, user):
        try:
            disposal, disposal_response = DisposalHelper.get_disposal_request_by_custom_id(custom_disposal_id, user.db_access)
            if disposal_response.status_code != status.HTTP_302_FOUND:
                return disposal_response
            ser = LightAssetDisposalSerializer(disposal, context=DisposalHelper.get_disposal_ser_context([disposal.id], user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_disposal(request_data, user):
        try:
            # get disposal request
            disposal_request, disposal_request_response = DisposalHelper.get_disposal_request_by_id(request_data.get("disposal_id"), user.db_access)
            if disposal_request_response.status_code != status.HTTP_302_FOUND:
                return disposal_request_response

            if not AssetHelper.check_asset_status_active(disposal_request.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            # update disposal request
            updated_disposal_request, is_important,  update_disposal_request_response = DisposalUpdater.update_disposal_fields(disposal_request, request_data, user)
            if update_disposal_request_response.status_code != status.HTTP_202_ACCEPTED:
                return update_disposal_request_response

            # create disposal record 
            if not DisposalHistory.create_asset_disposal_record_by_obj(updated_disposal_request, user.db_access):
                Logger.getLogger().error(CustomError.MHF_7)
                return Response(CustomError.get_full_error_json(CustomError.MHF_7), status=status.HTTP_400_BAD_REQUEST)

            if is_important:
                # ----------------- Email Vendor -------------------
                disposal_type_name = str(updated_disposal_request.disposal_type).capitalize()
                company_obj = CompanyHelper.get_list_companies(user.db_access)[0]
                html_message, notification_config = DisposalHelper.generate_appropriate_notification_email(
                    updated_disposal_request,
                    company_obj,
                    "update_disposal",
                    user,
                    is_update=True
                )

                vendor_email = updated_disposal_request.vendor_email
                if html_message is not None:
                    email_title = disposal_type_name + " (ID " + str(updated_disposal_request.id) + ") Has Been Updated - Auto-Generated email"

                    if notification_config.recipient_type == "auto":
                        managers = UserHelper.get_managers_emails_by_location(user.db_access, [DisposalHelper.get_disposal_location(updated_disposal_request)])
                        manager_list = [manager for manager in managers]
                        recipients = manager_list + [vendor_email]
                    else:
                        recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access) + [vendor_email]

                    email_response = Email.send_email_notification(recipients, email_title, html_message, [], html_content=True)
                    if email_response.status_code != status.HTTP_200_OK:
                        return email_response
                # --------------------------------------------------
                    
            # create disposal event log
            description = "Disposal request " + str(updated_disposal_request.custom_id) + " was updated."
            event_log_response = DisposalHistory.create_asset_disposal_event_log(updated_disposal_request, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            updated_disposal_request.save()

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_asset_disposals_trade_in_no_asset_request(user):
        try:
            non_null_disposals = list(AssetRequestHelper.get_all_non_null_ids(user.db_access))
            trade_ins = DisposalHelper.get_trade_ins(user.db_access)
            trade_in_no_disposal = trade_ins.exclude(id__in = non_null_disposals)
            disposals = DisposalHelper.select_related_to_disposal(trade_in_no_disposal)
            relevant_disposals = DisposalHelper.filter_disposal_for_user(disposals, user)
            disposal_id_list = relevant_disposals.values_list('id', flat=True)
            ser = LightAssetDisposalSerializer(relevant_disposals, many=True,
            context=DisposalHelper.get_disposal_ser_context(disposal_id_list, user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_disposal_status(request_data, file_specs, files, required_file_purposes, correct_disposal_type, user):
        try:
            # Checks ---------------------------------------------------------------------------------

            # check if all required files have been inputted and if they are the accepted file types
            if request_data.get("status").lower() == AssetDisposalModel.complete:
                file_validation_response = DisposalHelper.validate_files(required_file_purposes, file_specs.get("file_info"), files)
                if file_validation_response.status_code != status.HTTP_200_OK:
                    return file_validation_response

            # get disposal request
            disposal_request_obj, disposal_request_response = DisposalHelper.get_disposal_request_by_id(request_data.get("disposal_id"), user.db_access)
            if disposal_request_response.status_code != status.HTTP_302_FOUND:
                return disposal_request_response

            # check if disposal type is correct
            if disposal_request_obj.disposal_type.lower() != correct_disposal_type:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.ADUF_0))
                return Response(CustomError.get_full_error_json(CustomError.ADUF_0), status=status.HTTP_400_BAD_REQUEST)

            # check if new status is different to old status
            print(request_data.get("status").lower)
            if not DisposalHelper.is_status_new_by_obj(disposal_request_obj, request_data.get("status").lower()):
                Logger.getLogger().error(CustomError.SNN_0)
                return Response(CustomError.get_full_error_json(CustomError.SNN_0), status=status.HTTP_400_BAD_REQUEST)

            # check if refurbished --> check if the repair is complete if disposal is to be marked complete
            if disposal_request_obj.refurbished and request_data.get("status").lower() == AssetDisposalModel.complete:
                repair_obj, repair_response = RepairHelper.get_repair_request_by_disposal_id(disposal_request_obj.id, user.db_access)
                if repair_response.status_code == status.HTTP_302_FOUND:
                    repair_response
                if repair_obj.status != RepairsModel.delivered:
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.ADUF_3))
                    return Response(CustomError.get_full_error_json(CustomError.ADUF_3), status=status.HTTP_400_BAD_REQUEST)

            # Updates -------------------------------------------------------------------------------

            # update status
            disposal_request_obj, disposal_update_response = DisposalUpdater.edit_disposal_status(disposal_request_obj, request_data.get("status").lower())
            if disposal_update_response.status_code != status.HTTP_202_ACCEPTED:
                return disposal_update_response

            # set modified_by
            disposal_request_obj, modified_by_response = DisposalUpdater.update_disposal_request_modified_by(disposal_request_obj, user)
            if modified_by_response.status_code != status.HTTP_202_ACCEPTED:
                return modified_by_response

            # create disposal record 
            if not DisposalHistory.create_asset_disposal_record_by_obj(disposal_request_obj, user.db_access):
                Logger.getLogger().error(CustomError.MHF_7)
                return Response(CustomError.get_full_error_json(CustomError.MHF_7), status=status.HTTP_400_BAD_REQUEST)

            # create disposal event log
            description = "Disposal request " + str(disposal_request_obj.custom_id) + " status was set to " + str(request_data.get("status").lower()) + "."
            event_log_response = DisposalHistory.create_asset_disposal_event_log(disposal_request_obj, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            asset_obj = AssetHelper.get_asset_by_VIN(disposal_request_obj.VIN, user.db_access)
            if request_data.get("status").lower() == AssetDisposalModel.complete:
                asset_obj = AssetUpdater.update_asset_obj_status_with_history(asset_obj, AssetModel.Disposed)
                # upload files 
                upload_response = DisposalHandler.handle_add_supporting_files(disposal_request_obj, file_specs.get("file_info"), files, user)
                if upload_response.status_code != status.HTTP_200_OK:
                    return upload_response
            elif asset_obj.status.lower() == AssetModel.Disposed:
                asset_obj = AssetUpdater.update_asset_obj_status_with_history(asset_obj, AssetHelper.get_previous_different_status(asset_obj, user.db_access))

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_supporting_files(disposal_obj, file_specs, request_files, user):
        try:
            file_entries = []
            for _file in request_files:
                file_purpose = None
                expiration_date = None
                for info in file_specs:
                    if info.get("file_name") == _file.name:
                        file_purpose = info.get("purpose").lower()
                        expiration_date = info.get("expiration_date")

                # ------------ Upload files to blob --------------
                company_name = UserHelper.get_company_name_by_user_email(user.email, user.db_access)
                file_prefix = str(file_purpose.replace(" ", "_")) + "_" + str(disposal_obj.id) + "_"
                container = "disposal"

                file_status, file_info = BlobStorageHelper.write_file_to_blob(_file, container, file_prefix, company_name, user.db_access)
                if(not file_status):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_0))
                    return Response(CustomError.get_full_error_json(CustomError.FUF_0), status=status.HTTP_400_BAD_REQUEST)

                # ------------ Create file entry -----------------
                detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
                file_entry = DisposalUpdater.construct_disposal_file_instance(disposal_obj, file_info, file_purpose, expiration_date, detailed_user)

                file_entries.append(file_entry)

            # Upload file entries to db
            AssetDisposalFile.objects.using(user.db_access).bulk_create(file_entries)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

    # ----------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_update_company_directed_sale_disposal_status(request_data, file_specs, files, user):
        correct_disposal_type = AssetDisposalModel.company_directed_sale
        required_file_purposes = [AssetDisposalFile.bill_of_sale, AssetDisposalFile.method_of_payment, AssetDisposalFile.letter_of_release]
        return DisposalHandler.handle_update_disposal_status(request_data, file_specs, files, required_file_purposes, correct_disposal_type, user)

    # ----------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_update_auction_disposal_status(request_data, file_specs, files, user):
        correct_disposal_type = AssetDisposalModel.auction
        required_file_purposes = [AssetDisposalFile.bill_of_sale, AssetDisposalFile.method_of_payment]
        return DisposalHandler.handle_update_disposal_status(request_data, file_specs, files, required_file_purposes, correct_disposal_type, user)

    # ----------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_update_repurpose_disposal_status(request_data, file_specs, files, user):
        correct_disposal_type = AssetDisposalModel.repurpose
        required_file_purposes = []
        return DisposalHandler.handle_update_disposal_status(request_data, file_specs, files, required_file_purposes, correct_disposal_type, user)

    # ----------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_update_scrap_disposal_status(request_data, file_specs, files, user):
        correct_disposal_type = AssetDisposalModel.scrap
        required_file_purposes = [AssetDisposalFile.invoice, AssetDisposalFile.proceeds]
        return DisposalHandler.handle_update_disposal_status(request_data, file_specs, files, required_file_purposes, correct_disposal_type, user)

    # ----------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_update_donation_disposal_status(request_data, file_specs, files, user):
        correct_disposal_type = AssetDisposalModel.donate
        required_file_purposes = [AssetDisposalFile.tax_receipt]
        return DisposalHandler.handle_update_disposal_status(request_data, file_specs, files, required_file_purposes, correct_disposal_type, user)

    # ----------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_update_trade_in_disposal_status(request_data, file_specs, files, user):
        correct_disposal_type = AssetDisposalModel.trade_in
        required_file_purposes = [AssetDisposalFile.bill_of_sale, AssetDisposalFile.letter_of_release]
        return DisposalHandler.handle_update_disposal_status(request_data, file_specs, files, required_file_purposes, correct_disposal_type, user)

    # ----------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_update_transfer_disposal_status(request_data, file_specs, files, user):
        correct_disposal_type = AssetDisposalModel.transfer
        required_file_purposes = []
        return DisposalHandler.handle_update_disposal_status(request_data, file_specs, files, required_file_purposes, correct_disposal_type, user)

    # ----------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_update_write_off_disposal_status(request_data, file_specs, files, user):
        correct_disposal_type = AssetDisposalModel.write_off
        required_file_purposes = [AssetDisposalFile.insurance, AssetDisposalFile.total_loss_declaration]
        return DisposalHandler.handle_update_disposal_status(request_data, file_specs, files, required_file_purposes, correct_disposal_type, user)
