from core.AssetManager.AssetHelper import AssetHelper
from rest_framework.response import Response
from rest_framework import status
from .AssetRequestHelper import AssetRequestHelper
from .AssetRequestUpdater import AssetRequestUpdater
from ..ManufacturerManager.ManufacturerHelper import ManufacturerHelper
from ..EquipmentTypeManager.EquipmentTypeHelper import EquipmentTypeHelper
from ..HistoryManager.AssetRequestHistory import AssetRequestHistory
from ..AssetRequestJustificationManager.AssetRequestJustificationHelper import AssetRequestJustificationHelper
from ..BusinessUnitManager.BusinessUnitHelper import BusinessUnitHelper
from ..FileManager.PdfManager import PdfManager
from ..UserManager.UserHelper import UserHelper
from ..NotificationManager.NotificationHelper import NotificationHelper
from api.Models.asset_request import AssetRequestModel
from api.Models.asset_type import AssetTypeModel
from api.Serializers.serializers import AssetTypeSerializer, AssetManufacturerSerializer, LightEquipmentTypeSerializer, AssetRequestJustificationSerializer, AssetRequestSerializer, LightAssetRequestSerializer
from communication.EmailService.EmailService import Email
from GSE_Backend.errors.ErrorDictionary import CustomError
from datetime import datetime
import ast
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetRequestHandler():

    @staticmethod
    def handle_get_asset_types(user):
        try:
            asset_types = AssetTypeModel.objects.using(user.db_access).all().order_by('name')
            serializer = AssetTypeSerializer(asset_types, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_asset_type(asset_type_id, request_data, user):
        try:
            asset_type_obj = AssetTypeModel.objects.get(id=asset_type_id)
            serializer = AssetTypeSerializer(asset_type_obj, data=request_data, partial=True)

            if serializer.is_valid():
                detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
                serializer.save(modified_by=detailed_user, date_modified=datetime.now())
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except AssetTypeModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_asset_type_custom_field(asset_type_id, request_data, user):
        try:
            print("request_data: ", request_data)
            config_obj = AssetTypeModel.objects.get(id=asset_type_id)

            # Convert the custom_fields string to a dictionary
            custom_fields_dict = {}
            if config_obj.custom_fields:
                custom_fields_dict = ast.literal_eval(config_obj.custom_fields)

            # Update the custom_fields dictionary with the request_data
            custom_fields_dict.update(request_data)

            # Convert the updated custom_fields dictionary back to a string and update the AssetModel object
            updated_custom_fields = str(custom_fields_dict)
            config_obj.custom_fields = updated_custom_fields
            serializer = AssetTypeSerializer(config_obj, data=request_data, partial=True)
            if serializer.is_valid():
                detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
                serializer.save(modified_by=detailed_user, date_modified=datetime.now())
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print(f"Serializer Errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except AssetTypeModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(f"Exception occurred: {e}")
            return Response(status=status.HTTP_400_BAD_REQUEST)

    
    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_delete_asset_type_custom_field(asset_type_id, request_data, user):
        try:
            print("request_data: ", request_data)
            config_obj = AssetTypeModel.objects.get(id=asset_type_id)

            # Convert the custom_fields string to a dictionary
            custom_fields_dict = {}
            if config_obj.custom_fields:
                custom_fields_dict = ast.literal_eval(config_obj.custom_fields)

            # Update the custom_fields dictionary with the request_data
            keys = list(request_data.keys())
            for key in keys:
                if request_data[key] == None or len(request_data[key]) == 0:
                    del custom_fields_dict[key]
                else:
                    for subkey in request_data[key]:
                        del custom_fields_dict[key][subkey]    
                    if custom_fields_dict[key] == None or len(custom_fields_dict[key]) == 0:
                        del custom_fields_dict[key]

            # Convert the updated custom_fields dictionary back to a string and update the AssetModel object
            updated_custom_fields = str(custom_fields_dict)
            config_obj.custom_fields = updated_custom_fields
            serializer = AssetTypeSerializer(config_obj, data=request_data, partial=True)
            if serializer.is_valid():
                detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
                serializer.save(modified_by=detailed_user, date_modified=datetime.now())
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print(f"Serializer Errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except AssetTypeModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(f"Exception occurred: {e}")
            return Response(status=status.HTTP_400_BAD_REQUEST)

    
    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_manufacturer_by_asset_type(asset_id, user):
        try:
            queryset, get_response = ManufacturerHelper.get_manufacturer_by_asset_type(asset_id, user.db_access)
            if get_response.status_code != status.HTTP_302_FOUND:
                return get_response
            serializer = AssetManufacturerSerializer(queryset.order_by('name'), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_equipment(asset_id, manufacturer_id, user):
        try:
            queryset, get_response = EquipmentTypeHelper.get_equipment_type_by_asset_type_id_and_manufacturer(asset_id, manufacturer_id, user.db_access)
            if get_response.status_code != status.HTTP_302_FOUND:
                return get_response
            relevant_qs = EquipmentTypeHelper.select_related_to_equipment_type(queryset)
            ser = LightEquipmentTypeSerializer(relevant_qs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_justifications(user):
        try:
            queryset = AssetRequestJustificationHelper.get_all_justifications(user.db_access).order_by('name')
            ser = AssetRequestJustificationSerializer(queryset, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_asset_request(request_data, user):

        vin = request_data.get("VIN")
        if vin is not None:
            if not AssetHelper.check_asset_status_active(vin, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

        ser = AssetRequestSerializer(data=request_data)
        location_id, response = BusinessUnitHelper.get_business_unit_location_id(request_data.get('business_unit'), user.db_access)
        if response.status_code != status.HTTP_200_OK:
            return response
        request_data['location'] = location_id

        if ser.is_valid():
            asset_request_obj = ser.save()
            # update fields after db entry has been made
            asset_request_obj, created_by_status = AssetRequestUpdater.update_asset_request_post_creation(asset_request_obj, user)
            if created_by_status.status_code != status.HTTP_202_ACCEPTED:
                return created_by_status
        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
            return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors), status=status.HTTP_400_BAD_REQUEST)

        # create asset request record
        if not AssetRequestHistory.create_asset_request_record_by_obj(asset_request_obj):
            Logger.getLogger().error(CustomError.MHF_6)
            return Response(CustomError.get_full_error_json(CustomError.MHF_6), status=status.HTTP_400_BAD_REQUEST)

        # ----------------- Email Vendor -------------------
        notification_config, resp = NotificationHelper.get_notification_config_by_name("New Asset Request", user.db_access)
        if resp.status_code != status.HTTP_302_FOUND:
            return resp
        if notification_config.active and (
                notification_config.triggers is None or (
                        "add_asset_request" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                )
        ):
            fileInfo, htmlMessage = PdfManager.gen_asset_request_pdf_report(asset_request_obj, notification_config, user)
            email_title = "New Asset Request (ID " + str(asset_request_obj.id) + ") - Auto-Generated email"

            vendor_email = asset_request_obj.vendor_email
            if notification_config.recipient_type == "auto":
                recipients = [vendor_email]
            else:
                recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access) + [vendor_email]

            if(fileInfo is not None):
                email_response = Email.send_email_notification(recipients, email_title, htmlMessage, [fileInfo], html_content=True)
            else:
                email_response = Email.send_email_notification(recipients, email_title, htmlMessage, [], html_content=True)
            if email_response.status_code != status.HTTP_200_OK:
                AssetRequestModel.objects.using(user.db_access).filter(pk = asset_request_obj.id).delete()
                return email_response
        # --------------------------------------------------

        return Response(status=status.HTTP_201_CREATED)

    
    # ---------------------------------------------------------------------------------------------------------------------


    """@staticmethod
    def old_handle_add_asset_request(request_data, user):
        ser = AssetRequestSerializer(data=request_data)
        location_id, response = BusinessUnitHelper.get_business_unit_location_id(request_data.get('business_unit'), user.db_access)
        if response.status_code != status.HTTP_200_OK:
            return response
        request_data['location'] = location_id
        
        if(ser.is_valid()):
            asset_request_obj = ser.save()
            
            # update fields after db entry has been made
            asset_request_obj, created_by_status = AssetRequestUpdater.update_asset_request_post_creation(asset_request_obj, user)
            if created_by_status.status_code != status.HTTP_202_ACCEPTED:
                return created_by_status

            # create asset request record
            if(not AssetRequestHistory.create_asset_request_record_by_obj(asset_request_obj)):
                Logger.getLogger().error(CustomError.MHF_6)
                return Response(CustomError.get_full_error_json(CustomError.MHF_6), status=status.HTTP_400_BAD_REQUEST)

            # ----------------- Email Vendor -------------------
            notification_config, resp = NotificationHelper.get_notification_config_by_name("New Asset Request", user.db_access)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp
            if notification_config.active and (
                    notification_config.triggers is None or (
                        "add_asset_request" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                )
            ):
                fileInfo, htmlMessage = PdfManager.gen_asset_request_pdf_report(asset_request_obj, notification_config, user)
                email_title = "New Asset Request (ID " + str(asset_request_obj.id) + ") - Auto-Generated email"

                vendor_email = asset_request_obj.vendor_email
                if notification_config.recipient_type == "auto":
                    recipients = [vendor_email]
                else:
                    recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access) + [vendor_email]

                if(fileInfo is not None):
                    email_response = Email.send_email_notification(recipients, email_title, htmlMessage, [fileInfo], html_content=True)
                else:
                    email_response = Email.send_email_notification(recipients, email_title, htmlMessage, [], html_content=True)
                if email_response.status_code != status.HTTP_200_OK:
                    AssetRequestModel.objects.using(user.db_access).filter(pk = asset_request_obj.id).delete()
                    return email_response
            # --------------------------------------------------

            return Response(status=status.HTTP_201_CREATED)
        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
            return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors), status=status.HTTP_400_BAD_REQUEST)
    """

    # --------------------------------------------------------------------------------------------------------------------- 
      
    @staticmethod
    def handle_list_in_progress_asset_requests(user):
        try:
            queryset = AssetRequestHelper.select_related_to_asset_request(AssetRequestHelper.get_in_progress_asset_requests(user.db_access))
            relevant_qs = AssetRequestHelper.filter_asset_requests_for_user(queryset, user)
            ser = LightAssetRequestSerializer(relevant_qs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_list_delivered_asset_requests(user):
        try:
            queryset = AssetRequestHelper.select_related_to_asset_request(AssetRequestHelper.get_delivered_asset_requests(user.db_access))
            relevant_qs = AssetRequestHelper.filter_asset_requests_for_user(queryset, user)
            ser = LightAssetRequestSerializer(relevant_qs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_asset_request_details_by_id(asset_request_id, user):
        try:
            asset_request_obj, get_response = AssetRequestHelper.get_asset_request_by_id(asset_request_id, user.db_access)
            if get_response.status_code != status.HTTP_302_FOUND:
                return get_response
                
            asset_request = asset_request_obj
            ser = LightAssetRequestSerializer(asset_request)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_asset_request_details_by_custom_id(asset_request_custom_id, user):
        try:
            asset_request_obj, get_response = AssetRequestHelper.get_asset_request_by_custom_id(asset_request_custom_id, user.db_access)
            if get_response.status_code != status.HTTP_302_FOUND:
                return get_response
                
            asset_request = asset_request_obj
            ser = LightAssetRequestSerializer(asset_request)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_asset_request_delivered(asset_request_obj, request_data, user):
        # Front-End should call API that adds asset before this.
        try:
            # check if VIN doesn't exist
            if not AssetHelper.asset_exists(request_data.get('vin'), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.VDNE_0))
                return asset_request_obj, Response(CustomError.get_full_error_json(CustomError.VDNE_0), status=status.HTTP_400_BAD_REQUEST)

            asset_request_obj.status = AssetRequestModel.delivered
            asset_request_obj.VIN = AssetHelper.get_asset_by_VIN(request_data.get('vin'), user.db_access)
            asset_request_obj.save()
            return asset_request_obj, Response(status=status.HTTP_200_OK)
        
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return asset_request_obj, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_asset_request_cancelled(asset_request_obj, user):
        try:
            # set the maintenance object status to cancelled
            asset_request_obj.status = AssetRequestModel.cancelled
            asset_request_obj.save()

            # email vendor
            # TODO: so much copying+pasting for these. do something about this later?
            
            notification_config, resp = NotificationHelper.get_notification_config_by_name("Request Cancellation", user.db_access)
            if resp.status_code != status.HTTP_302_FOUND:
                return resp
            if notification_config.active and (
                notification_config.triggers is None or (
                    "cancel_asset_request" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                )
            ):
                file_info, html_message = PdfManager.gen_asset_request_pdf_report(asset_request_obj, notification_config, user, is_cancel=True)
                email_title = "Asset Request (ID " + str(asset_request_obj.id) + ") Has Been Cancelled - Auto-Generated Email"
                managers = UserHelper.get_managers_emails_by_location(user.db_access, [asset_request_obj.business_unit.location.location_id])
                
                vendor_email = updated_asset_request.vendor_email
                if notification_config.recipient_type == "auto":
                    manager_list = [manager for manager in managers]
                    recipients = manager_list + [vendor_email]
                else:
                    recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access) + [vendor_email]

                if(file_info is not None):
                    email_response = Email.send_email_notification(recipients, email_title, html_message, [file_info], html_content=True)
                else:
                    email_response = Email.send_email_notification(recipients, email_title, html_message, [], html_content=True)
                if email_response.status_code != status.HTTP_200_OK:
                    return email_response
            # --------------------------------------------------

            # return the response - updated maintenance object
            return asset_request_obj, Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return asset_request_obj, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_asset_request_generic_status(asset_request_obj, new_status):
        try:
            asset_request_obj.status = new_status
            asset_request_obj.save()
            return asset_request_obj, Response(status=status.HTTP_200_OK)
        
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return asset_request_obj, Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_update_asset_request_status(request_data, user):
        try:
            new_status = str(request_data.get('status')).lower()

            # check if new status is valid
            if not AssetRequestHelper.is_status_valid(new_status):
                Logger.getLogger().error(CustomError.IS_0)
                return Response(CustomError.get_full_error_json(CustomError.IS_0), status=status.HTTP_400_BAD_REQUEST)

            # get asset request object
            asset_request_obj, asset_request_response = AssetRequestHelper.get_asset_request_by_id(request_data.get('asset_request_id'), user.db_access)
            if asset_request_response.status_code != status.HTTP_302_FOUND:
                return asset_request_response

            if asset_request_obj.VIN is not None:
                if not AssetHelper.check_asset_status_active(asset_request_obj.VIN, user.db_access):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                       CustomError.get_error_user(CustomError.TUF_16)))
                    return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                    CustomError.get_error_user(CustomError.TUF_16)),
                                    status=status.HTTP_400_BAD_REQUEST)

            original_status = str(asset_request_obj.status).lower()

            # check if new status is new
            if new_status == original_status:
                Logger.getLogger().error(CustomError.SNN_0)
                return Response(CustomError.get_full_error_json(CustomError.SNN_0), status=status.HTTP_400_BAD_REQUEST)

            # update status
            if new_status == AssetRequestModel.delivered.lower():
                asset_request_obj, update_response = AssetRequestHandler.handle_asset_request_delivered(asset_request_obj, request_data, user)
            elif new_status == AssetRequestModel.cancelled.lower():
                asset_request_obj, update_response = AssetRequestHandler.handle_asset_request_cancelled(asset_request_obj, user)
            else:
                asset_request_obj, update_response = AssetRequestHandler.handle_asset_request_generic_status(asset_request_obj, new_status)

            if update_response.status_code != status.HTTP_200_OK:
                return update_response

            # set modified_by
            asset_request_obj, created_by_status = AssetRequestUpdater.update_asset_request_modified_by(asset_request_obj, user)
            if created_by_status.status_code != status.HTTP_202_ACCEPTED:
                return created_by_status

            # create asset request record
            if(not AssetRequestHistory.create_asset_request_record_by_obj(asset_request_obj)):
                Logger.getLogger().error(CustomError.MHF_6)
                return Response(CustomError.get_full_error_json(CustomError.MHF_6), status=status.HTTP_400_BAD_REQUEST)
            
            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_asset_request(request_data, user):
        try:
            # get asset request
            asset_request, asset_request_response = AssetRequestHelper.get_asset_request_by_id(request_data.get("asset_request_id"), user.db_access)
            if asset_request_response.status_code != status.HTTP_302_FOUND:
                return asset_request_response

            if asset_request.VIN is not None:
                if not AssetHelper.check_asset_status_active(asset_request.VIN, user.db_access):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                       CustomError.get_error_user(CustomError.TUF_16)))
                    return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                    CustomError.get_error_user(CustomError.TUF_16)),
                                    status=status.HTTP_400_BAD_REQUEST)

            # update asset request
            updated_asset_request, is_important, update_asset_request_response = AssetRequestUpdater.update_asset_request_fields(asset_request, request_data, user)
            if update_asset_request_response.status_code != status.HTTP_202_ACCEPTED:
                return update_asset_request_response

            if is_important:
                # ----------------- Email Vendor -------------------
                notification_config, resp = NotificationHelper.get_notification_config_by_name("New Asset Request", user.db_access)
                if resp.status_code != status.HTTP_302_FOUND:
                    return resp
                if notification_config.active and (
                    notification_config.triggers is None or (
                        "update_asset_request" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                    )
                ):
                    file_info, html_message = PdfManager.gen_asset_request_pdf_report(updated_asset_request, notification_config, user, is_update=True)
                    email_title = "Asset Request (ID " + str(updated_asset_request.id) + ") Has Been Updated - Auto-Generated Email"
                    managers = UserHelper.get_managers_emails_by_location(user.db_access, [updated_asset_request.business_unit.location.location_id])
                    
                    vendor_email = updated_asset_request.vendor_email
                    if notification_config.recipient_type == "auto":
                        manager_list = [manager for manager in managers]
                        recipients = manager_list + [vendor_email]
                    else:
                        recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access) + [vendor_email]

                    if(file_info is not None):
                        email_response = Email.send_email_notification(recipients, email_title, html_message, [file_info], html_content=True)
                    else:
                        email_response = Email.send_email_notification(recipients, email_title, html_message, [], html_content=True)
                    if email_response.status_code != status.HTTP_200_OK:
                        return email_response
                # --------------------------------------------------

            # create asset request record
            if(not AssetRequestHistory.create_asset_request_record_by_obj(asset_request)):
                Logger.getLogger().error(CustomError.MHF_6)
                return Response(CustomError.get_full_error_json(CustomError.MHF_6), status=status.HTTP_400_BAD_REQUEST)

            updated_asset_request.save()

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
        
