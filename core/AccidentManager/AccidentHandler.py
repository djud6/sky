from core.PusherManager.PusherHelper import PusherHelper
from core.UserManager.UserHelper import UserHelper
from rest_framework.response import Response
from rest_framework import status
from api.Models.accident_report import AccidentModel
from api.Models.asset_model import AssetModel
from api.Models.asset_log import AssetLog
from core.Helper import HelperMethods
from .AccidentUpdater import AccidentUpdater
from .AccidentHelper import AccidentHelper
from ..FileManager.FileHelper import FileHelper
from ..BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from api.Models.DetailedUser import DetailedUser
from ..AssetManager.AssetUpdater import AssetUpdater
from ..AssetManager.AssetHelper import AssetHelper
from ..RepairManager.RepairHelper import RepairHelper
from ..IssueManager.IssueHelper import IssueHelper
from ..NotificationManager.NotificationHelper import NotificationHelper
from ..HistoryManager.AssetHistory import AssetHistory
from ..HistoryManager.AccidentHistory import AccidentHistory
from api.Serializers.serializers import LightAccidentSerializer, AccidentSerializer
from core.FileManager.PdfManager import PdfManager
from communication.EmailService.EmailService import Email
from GSE_Backend.errors.ErrorDictionary import CustomError
from datetime import datetime
from django.utils import timezone
from core.ChartCalculations.ChartCalculations import ChartCalculations
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AccidentHandler():

    @staticmethod
    def handle_get_accident_by_VIN(_vin, user):
        try:
            queryset = AccidentHelper.get_accidents_by_vin(_vin, user.db_access)
            relevant_qs = AccidentHelper.select_related_to_accident(AccidentHelper.filter_accidents_for_user(queryset, user))
            accident_id_list = queryset.values_list('accident_id', flat=True)
            ser = LightAccidentSerializer(relevant_qs, many=True, context=AccidentHelper.get_accident_ser_context(accident_id_list, user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_accident(request, user):

        if not AssetHelper.check_asset_status_active(
                HelperMethods.json_str_to_dict(request.POST['data']).get("VIN"), user.db_access):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                               CustomError.get_error_user(CustomError.TUF_16)))
            return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                            CustomError.get_error_user(CustomError.TUF_16)),
                            status=status.HTTP_400_BAD_REQUEST)

        data = AccidentHelper.update_accident_dict(HelperMethods.json_str_to_dict(request.POST['data']), user.db_access)
        ser = AccidentSerializer(data=data)
        files = request.FILES.getlist('files')
        if(ser.is_valid()):

            accident_obj = ser.save()
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            # update fields after db entry has been made
            accident_obj, update_status = AccidentUpdater.update_accident_post_creation(accident_obj, user)
            if update_status.status_code != status.HTTP_202_ACCEPTED:
                return update_status

            # create accident report record
            company_name = detailed_user.company.company_name
            channel_name = company_name
            pusher_payload = {'location': accident_obj.location.location_id}
            history_func = AccidentHistory.create_accident_report_record
            pusher_helper = PusherHelper(channel_name, PusherHelper.AccidentCreatedEvent, pusher_payload, False, history_func)
            if(not pusher_helper.push(accident_obj.accident_id, user.db_access)):
                Logger.getLogger().error(CustomError.MHF_3)
                return Response(CustomError.get_full_error_json(CustomError.MHF_3), status=status.HTTP_400_BAD_REQUEST)

            # create accident event log
            description = "Accident " + str(accident_obj.custom_id) + " was reported."
            event_log_response = AccidentHistory.create_accident_event_log(accident_obj, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            #update asset last process
            AssetUpdater.update_last_process(ser.validated_data.get("VIN"), AssetModel.Accident)

            if not accident_obj.is_operational and not AssetHelper.asset_is_inop(accident_obj.VIN, user.db_access):
                #Update asset status
                AssetUpdater.update_asset_status(ser.validated_data.get("VIN"), AssetModel.Inop)

                # create asset record 
                asset_obj = AssetHelper.get_asset_by_VIN(ser.validated_data.get("VIN"), user.db_access)
                if(not AssetHistory.create_asset_record_by_obj(asset_obj)):
                    Logger.getLogger().error(CustomError.MHF_0)
                    return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

                # create asset event log
                description = "Asset was set to inoperative and last proccess was set to " + str(AssetLog.accident) + " " + str(accident_obj.custom_id) + "."
                event_log_response = AccidentHistory.create_accident_event_log(accident_obj, description)
                if event_log_response.status_code != status.HTTP_201_CREATED:
                    return event_log_response

            try:
                # -------------- Email accident report ---------------
                notification_config, resp = NotificationHelper.get_notification_config_by_name("New Accident", user.db_access)
                if resp.status_code != status.HTTP_302_FOUND:
                    return resp
                if notification_config.active and (
                    notification_config.triggers is None or (
                        "add_accident" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                    )
                ):
                    fileInfo, htmlMessage = PdfManager.gen_accident_pdf_report(accident_obj, notification_config, user)
                    email_title = "Newly Reported Accident (ID " + str(accident_obj.accident_id) + ")"

                    if notification_config.recipient_type == "auto":
                        recipients = AssetHelper.get_asset_managers_emails(ser.validated_data.get("VIN"), user.db_access)
                    else:
                        recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access)

                    if(fileInfo is not None):
                        email_response = Email.send_email_notification(recipients, email_title, htmlMessage, [fileInfo], html_content=True)
                    else:
                        email_response = Email.send_email_notification(recipients, email_title, htmlMessage, [], html_content=True)
                    if email_response.status_code != status.HTTP_200_OK:
                        AccidentModel.objects.using(user.db_access).filter(accident_id=accident_obj.accident_id).delete()
                        return email_response
                # ----------------------------------------------------

            except Exception as e:
                AccidentModel.objects.using(user.db_access).filter(accident_id=accident_obj.accident_id).delete()
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
                return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

            try:
                # -------------- Verify file types ----------------
                valid_file_types = ["application/pdf", "image/jpeg", "image/png", "image/heic", "image/heif"]
                if(not FileHelper.verify_files_are_accepted_types(files, valid_file_types)):
                    AccidentModel.objects.using(user.db_access).filter(accident_id=accident_obj.accident_id).delete()
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.IUF_1))
                    return Response(CustomError.get_full_error_json(CustomError.IUF_1), status=status.HTTP_400_BAD_REQUEST)

                # ------------ Upload files to blob --------------               
                company_name = DetailedUser.objects.get(email=request.user.email).company.company_name
                file_suffix = "Accident_" + str(accident_obj.accident_id) + "_"
                image_status, file_infos = BlobStorageHelper.write_files_to_blob(files, "accidents", file_suffix, company_name, request.user.db_access)
                if(not image_status):
                    AccidentModel.objects.using(user.db_access).filter(accident_id=accident_obj.accident_id).delete()
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.IUF_0))
                    return Response(CustomError.get_full_error_json(CustomError.IUF_0), status=status.HTTP_400_BAD_REQUEST)

                # ----------- Upload file urls to DB -------------
                if(not AccidentUpdater.create_accident_file_record(accident_obj, file_infos, request.user.db_access)):
                    AccidentModel.objects.using(user.db_access).filter(accident_id=accident_obj.accident_id).delete()
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.IUF_0))
                    return Response(CustomError.get_full_error_json(CustomError.IUF_0), status=status.HTTP_400_BAD_REQUEST)
                return Response({"accident_id":accident_obj.accident_id},status=status.HTTP_201_CREATED)

            except Exception as e:
                AccidentModel.objects.using(user.db_access).filter(accident_id=accident_obj.accident_id).delete()
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
                return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)



        else:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
            return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_set_notification_status(request_data, user):
        accident_id = request_data.get("accident_id")
        value = request_data.get("notification_ack")
        try:
            accident_obj = AccidentModel.objects.using(user.db_access).get(pk=accident_id)

            if not AssetHelper.check_asset_status_active(accident_obj.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            bool_value = HelperMethods.validate_bool(value) # In case bool variable is lower case in URL
            accident_obj.notification_ack = bool_value
            accident_obj.save()

            # set modified_by
            accident_obj, modified_by_status = AccidentUpdater.update_accident_modified_by(accident_obj, user)
            if modified_by_status.status_code != status.HTTP_202_ACCEPTED:
                return modified_by_status

            # create accident report record
            if(not AccidentHistory.create_accident_report_record(accident_obj.accident_id, user.db_access)):
                Logger.getLogger().error(CustomError.MHF_3)
                return Response(CustomError.get_full_error_json(CustomError.MHF_3), status=status.HTTP_400_BAD_REQUEST)

            # create accident event log
            description = "Accident " + str(accident_obj.custom_id) + " notification acknowledged status was set to " + str(bool_value) + "."
            event_log_response = AccidentHistory.create_accident_event_log(accident_obj, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            return Response(status=status.HTTP_200_OK)
        except AccidentModel.DoesNotExist:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ADNE_0))
            return Response(CustomError.get_full_error_json(CustomError.ADNE_0), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
            
    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_set_accident_report_status(request):
        accident_id = request.data.get("accident_id")
        value = request.data.get("accident_report_completed")
        try:
            accident_obj = AccidentModel.objects.using(request.user.db_access).get(pk=accident_id)

            if not AssetHelper.check_asset_status_active(accident_obj.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            bool_value = HelperMethods.validate_bool(value) # In case bool variable is lower case in URL
            accident_obj.accident_report_completed = bool_value
            accident_obj.save()

            # set modified_by
            accident_obj, modified_by_status = AccidentUpdater.update_accident_modified_by(accident_obj, request.user)
            if modified_by_status.status_code != status.HTTP_202_ACCEPTED:
                return modified_by_status

            # create accident report record and send pusher event
            if(not AccidentHistory.create_accident_report_record(accident_obj.accident_id, request.user.db_access)):
                Logger.getLogger().error(CustomError.MHF_3)
                return Response(CustomError.get_full_error_json(CustomError.MHF_3), status=status.HTTP_400_BAD_REQUEST)

            # create accident event log
            description = "Accident " + str(accident_obj.custom_id) + " completion status was set to " + str(bool_value) + "."
            event_log_response = AccidentHistory.create_accident_event_log(accident_obj, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            return Response(status=status.HTTP_200_OK)
        except AccidentModel.DoesNotExist:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ADNE_0))
            return Response(CustomError.get_full_error_json(CustomError.ADNE_0), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
        
    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_mark_accident_status_to_resolved(accident_id, user):
        try:
            accident_obj = AccidentModel.objects.using(user.db_access).get(pk=accident_id)

            if not AssetHelper.check_asset_status_active(accident_obj.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            old_status = accident_obj.is_resolved
            accident_obj.is_resolved = True
            accident_obj.save()
            
            # set modified_by
            accident_obj, created_by_status = AccidentUpdater.update_accident_modified_by(accident_obj, user)
            if created_by_status.status_code != status.HTTP_202_ACCEPTED:
                return created_by_status

            # -------------- Pusher -----------------
            event_name = None
            pusher_payload = {'location': accident_obj.location.location_id}
            event_name = PusherHelper.AccidentResolvedEvent
            skip_push = False
            if old_status == accident_obj.is_resolved:
                skip_push = True

            channel_name = DetailedUser.objects.get(email=user.email).company.company_name
            history_func = AccidentHistory.create_accident_report_record
            pusher_helper = PusherHelper(channel_name, event_name, pusher_payload, skip_push, history_func)

            # create accident report record and send pusher event
            if event_name is not None:
                if not pusher_helper.push(accident_id, user.db_access):
                    Logger.getLogger().error(CustomError.MHF_3)
                    return Response(CustomError.get_full_error_json(CustomError.MHF_3), status=status.HTTP_400_BAD_REQUEST)

            # create accident event log
            description = "Accident " + str(accident_obj.custom_id) + " was resolved."
            event_log_response = AccidentHistory.create_accident_event_log(accident_obj, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            return Response(status=status.HTTP_200_OK)
        except AccidentModel.DoesNotExist:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ADNE_0))
            return Response(CustomError.get_full_error_json(CustomError.ADNE_0), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_list_accident_by_date(request_data, user):
        date_range_start = request_data.get("start_date")
        date_range_end = request_data.get("end_date")
        try:
            queryset = AccidentHelper.select_related_to_accident(AccidentModel.objects.using(user.db_access).filter(date_created__range=[date_range_start, date_range_end]))
            relevant_qs = AccidentHelper.filter_accidents_for_user(queryset, user)
            accident_id_list = queryset.values_list('accident_id', flat=True)
            ser = LightAccidentSerializer(relevant_qs, many=True, context=AccidentHelper.get_accident_ser_context(accident_id_list, user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_accident_count_unresolved(user):
        try:
            queryset = AccidentModel.objects.using(user.db_access).filter(is_resolved=False)
            count = AccidentHelper.filter_accidents_for_user(queryset, user).count()
            return Response({"count":count}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_accident_count_resolved(user):
        try:
            queryset = AccidentModel.objects.using(user.db_access).filter(is_resolved=True)
            count = AccidentHelper.filter_accidents_for_user(queryset, user).count()
            return Response({"count":count}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_accident_percentage_resolved(user):
        try:
            total_qs = AccidentModel.objects.using(user.db_access).all()
            count_total = AccidentHelper.filter_accidents_for_user(total_qs, user).count()
            resolved_qs = AccidentModel.objects.using(user.db_access).filter(is_resolved=True)
            count_resolved = AccidentHelper.filter_accidents_for_user(resolved_qs, user).count()
            percentageResolved = round((count_resolved / count_total) * 100, 2)
            return Response({"resolved_percent":percentageResolved}, status=status.HTTP_200_OK)
        except ZeroDivisionError as zde:
            Logger.getLogger().error(zde)
            return Response({"resolved_percent":0}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_accident_details_by_id(accident_id, user):
        try:
            accident, accident_response = AccidentHelper.get_accident_by_id(accident_id, user.db_access)
            if accident_response.status_code != status.HTTP_302_FOUND:
                return accident_response
            ser = LightAccidentSerializer(accident, context=AccidentHelper.get_accident_ser_context([accident.accident_id], user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_accident_averages(user, start_date=None, end_date=None):
        try:
            queryset = AccidentHelper.get_all_accidents(user.db_access)
            filtered_queryset = AccidentHelper.filter_accidents_for_user(queryset, user)

            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                filtered_queryset = filtered_queryset.filter(date_created__gte=start_date)

            if end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                filtered_queryset = filtered_queryset.filter(date_created__lte=end_date)

            total_count = filtered_queryset.count()
            preventable_count = filtered_queryset.filter(is_preventable=1).count()
            non_preventable_count = total_count - preventable_count

            average_total_count = total_count / AssetModel.objects.count()
            average_preventable_count = preventable_count / AssetModel.objects.count()
            average_non_preventable_count = non_preventable_count / AssetModel.objects.count()

            return Response({
                "average_total_count": average_total_count,
                "average_preventable_count": average_preventable_count,
                "average_non_preventable_count": average_non_preventable_count
            }, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.ADNE_0))
            return Response(CustomError.get_full_error_json(CustomError.ADNE_0), status=status.HTTP_400_BAD_REQUEST)


    
    @staticmethod
    def handle_get_accident_details_by_custom_id(custom_accident_id, user):
        try:
            accident, accident_response = AccidentHelper.get_accident_by_custom_id(custom_accident_id, user.db_access)
            if accident_response.status_code != status.HTTP_302_FOUND:
                return accident_response
            ser = LightAccidentSerializer(accident, context=AccidentHelper.get_accident_ser_context([accident.accident_id], user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_accident_list(user):
        try:
            accidents = AccidentHelper.select_related_to_accident(AccidentModel.objects.using(user.db_access).all())
            relevant_accident = IssueHelper.filter_issues_for_user(accidents, user)
            accident_id_list = relevant_accident.values_list('accident_id', flat=True)
            ser = LightAccidentSerializer(relevant_accident,many=True,context=AccidentHelper.get_accident_ser_context(accident_id_list, user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_accident_downtime_for_asset(vin, user):
        try:
            relevant_accidents = AccidentHelper.get_accidents_by_vin(vin, user.db_access)
            preventable_downtime, non_preventable_downtime = AccidentHelper.get_downtime_for_accidents(relevant_accidents, user.db_access)

            try:
                percent_non_preventable = (non_preventable_downtime / (preventable_downtime + non_preventable_downtime)) * 100
                percent_preventable = 100 - percent_non_preventable
            except ZeroDivisionError as zde:
                Logger.getLogger().error(zde)
                return Response({"non_preventable_hours": 0, "preventable_hours": 0, "percent_non_preventable": 0, "percent_preventable": 0}, status=status.HTTP_200_OK)

            return Response({"non_preventable_hours": non_preventable_downtime, "preventable_hours": preventable_downtime, "percent_non_preventable": percent_non_preventable, "percent_preventable": percent_preventable}, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_accident_downtime_for_fleet(user):
        try:
            
            total_preventable_downtime = 0
            total_non_preventable_downtime = 0

            all_accidents = AccidentHelper.get_all_accidents(user.db_access)
            total_preventable_downtime, total_non_preventable_downtime = AccidentHelper.get_downtime_for_accidents(all_accidents, user.db_access)

            try:
                percent_non_preventable = (total_non_preventable_downtime / (total_preventable_downtime + total_non_preventable_downtime)) * 100
                percent_preventable = 100 - percent_non_preventable
            except ZeroDivisionError as zde:
                Logger.getLogger().error(zde)
                return Response({"non_preventable_hours": 0, "preventable_hours": 0, "percent_non_preventable": 0, "percent_preventable": 0}, status=status.HTTP_200_OK)

            return Response({"non_preventable_hours": total_non_preventable_downtime, "preventable_hours": total_preventable_downtime, "percent_non_preventable": percent_non_preventable, "percent_preventable": percent_preventable}, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_update_accident(request_data, user):
        try:
            # get accident
            accident, accident_response = AccidentHelper.get_accident_by_id(request_data.get("accident_id"), user.db_access)
            if accident_response.status_code != status.HTTP_302_FOUND:
                return accident_response

            if not AssetHelper.check_asset_status_active(accident.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            # update accident
            updated_accident, is_important, update_accident_response = AccidentUpdater.update_accident_fields(accident, request_data, user)
            if update_accident_response.status_code != status.HTTP_202_ACCEPTED:
                return update_accident_response

            # create accident report record
            if(not AccidentHistory.create_accident_report_record(updated_accident.accident_id, user.db_access)):
                Logger.getLogger().error(CustomError.MHF_3)
                return Response(CustomError.get_full_error_json(CustomError.MHF_3), status=status.HTTP_400_BAD_REQUEST)

            # create accident event log
            description = "Accident " + str(updated_accident.custom_id) + " was updated."
            event_log_response = AccidentHistory.create_accident_event_log(updated_accident, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response
            
            if is_important:
                # -------------- Email accident report ---------------
                notification_config, resp = NotificationHelper.get_notification_config_by_name("New Accident", user.db_access)
                if resp.status_code != status.HTTP_302_FOUND:
                    return resp
                if notification_config.active and (
                    notification_config.triggers is None or (
                        "update_accident" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                    )
                ):
                    file_info, html_message = PdfManager.gen_accident_pdf_report(accident, user, notification_config, is_update=True)
                    email_title = "Accident Report (ID " + str(updated_accident.accident_id) + ")" + " Has Been Updated - Auto-Generated Email"

                    if notification_config.recipient_type == "auto":
                        recipients = UserHelper.get_managers_emails_by_location(user.db_access, [AccidentHelper.get_accident_location(updated_accident)])
                    else:
                        recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access)

                    email_response = Email.send_email_notification(recipients, email_title, html_message, [], html_content=True)
                    if email_response.status_code != status.HTTP_200_OK:
                        return email_response
                # ----------------------------------------------------
                
            updated_accident.save()

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
          
    # ---------------------------------------------------------------------------------------------------------------------
        
    @staticmethod
    def handle_get_asset_downtime_date_range(start_date, end_date, user):
        try:
            start_date_obj = timezone.make_aware(datetime.strptime(start_date, '%m-%d-%Y'))
            end_date_obj = timezone.make_aware(datetime.strptime(end_date, '%m-%d-%Y'))

            accidents_vins = AccidentModel.objects.filter(date_created__range=[start_date_obj, end_date_obj]).values_list('VIN_id', flat=True).distinct()

            all_accidents = AccidentModel.objects.using(user.db_access).filter(VIN__VIN__in=accidents_vins)

            preventable_downtime, non_preventable_downtime = AccidentHelper.get_downtime_for_accidents_list(all_accidents, user.db_access)
            preventable_hours = preventable_downtime.total_seconds() // 3600
            non_preventable_hours = non_preventable_downtime.total_seconds() // 3600

            total_downtime = preventable_downtime + non_preventable_downtime

            if total_downtime.total_seconds() == 0:
                percent_preventable = 0
                percent_non_preventable = 0
            else:
                percent_preventable = (preventable_downtime / total_downtime) * 100
                percent_non_preventable = (non_preventable_downtime / total_downtime) * 100

            # Calculate repair_hours and maintenance_hours here
            repair_hours = ChartCalculations.total_repair_hours(start_date_obj, end_date_obj, user)
            maintenance_hours = ChartCalculations.total_maintenance_hours(start_date_obj, end_date_obj, user)

            return Response({
                "maintenance_hours": maintenance_hours,
                "repair_hours": repair_hours,
                "non_preventable_hours": non_preventable_hours,
                "preventable_hours": preventable_hours,
                "percent_non_preventable": percent_non_preventable,
                "percent_preventable": percent_preventable
            }, status=status.HTTP_200_OK)

        except ZeroDivisionError as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response({
                "maintenance_hours": 0,
                "repair_hours": 0,
                "non_preventable_hours": 0,
                "preventable_hours": 0,
                "percent_non_preventable": 0,
                "percent_preventable": 0
            }, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
