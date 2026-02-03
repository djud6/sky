from core.PusherManager.PusherHelper import PusherHelper
from core.RepairManager.RepairHelper import RepairHelper
from rest_framework.response import Response
from rest_framework import status
from ..Helper import HelperMethods
from .IssueUpdater import IssueUpdater
from .IssueHelper import IssueHelper
from ..FileManager.FileHelper import FileHelper
from ..BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from ..NotificationManager.NotificationHelper import NotificationHelper
from ..HistoryManager.IssueHistory import IssueHistory
from ..AssetManager.AssetHelper import AssetHelper
from api.Models.asset_issue import AssetIssueModel
from api.Models.DetailedUser import DetailedUser
from ..UserManager.UserHelper import UserHelper
from api.Models.accident_report import AccidentModel
from api.Serializers.serializers import IssueSerializer, LightIssueSerializer
from ..FileManager.PdfManager import PdfManager
from communication.EmailService.EmailService import Email
from GSE_Backend.errors.ErrorDictionary import CustomError
from django.core.exceptions import ObjectDoesNotExist
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class IssueHandler():
    
    @staticmethod
    def handle_add_issue(request_data, files, user):
        try:

            if not AssetHelper.check_asset_status_active(request_data.get("VIN"), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            request_data = IssueHelper.update_issue_dict(request_data, user.db_access)
            serializer = IssueSerializer(data=request_data)
            if serializer.is_valid():
                issue_obj = serializer.save()
                db_name = user.db_access
                detailed_user = UserHelper.get_detailed_user_obj(user.email, db_name)

                try:
                    # -------------- Verify file types ----------------
                    valid_issue_file_types = ["application/pdf", "text/plain", "image/jpeg", "image/png", "image/heic", "image/heif"]
                    if(not FileHelper.verify_files_are_accepted_types(files, valid_issue_file_types)):
                        AssetIssueModel.objects.filter(issue_id=issue_obj.issue_id).delete()
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.IUF_1))
                        return Response(CustomError.get_full_error_json(CustomError.IUF_1), status=status.HTTP_400_BAD_REQUEST)

                    # ------------ Upload files to blob --------------
                    company_name = DetailedUser.objects.get(email=user.email).company.company_name
                    file_suffix = "Issue_" + str(issue_obj.issue_id) + "_"
                    image_status, files_infos = BlobStorageHelper.write_files_to_blob(files, "issues", file_suffix, company_name, user.db_access)
                    if(not image_status):
                        AssetIssueModel.objects.filter(issue_id=issue_obj.issue_id).delete()
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.IUF_0))
                        return Response(CustomError.get_full_error_json(CustomError.IUF_0), status=status.HTTP_400_BAD_REQUEST)

                    # ----------- Upload file urls to DB --------------
                    if(not IssueUpdater.create_issue_file_record(issue_obj, files_infos, user.db_access)):
                        AssetIssueModel.objects.filter(issue_id=issue_obj.issue_id).delete()
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.IUF_0))
                        return Response(CustomError.get_full_error_json(CustomError.IUF_0), status=status.HTTP_400_BAD_REQUEST)

                    # -------------- Email issue report ---------------
                    notification_config, resp = NotificationHelper.get_notification_config_by_name("New Asset Issue", user.db_access)
                    if resp.status_code != status.HTTP_302_FOUND:
                        return resp
                    if notification_config.active and (
                    notification_config.triggers is None or (
                            "add_issue" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                        )
                    ):
                        fileInfo, htmlMessage = PdfManager.gen_issue_pdf_report(issue_obj, notification_config, user)
                        email_title = "Newly Reported Issue (ID " + str(issue_obj.issue_id) + ") - Auto-Generated Email"
                        if notification_config.recipient_type == "auto":
                            recipients = AssetHelper.get_asset_managers_emails(serializer.validated_data.get("VIN"), user.db_access)
                        else:
                            recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access)
                        if(fileInfo is not None):
                            email_response = Email.send_email_notification(recipients, email_title, htmlMessage, [fileInfo], html_content=True)
                        else:
                            email_response = Email.send_email_notification(recipients, email_title, htmlMessage, [], html_content=True)
                        if email_response.status_code != status.HTTP_200_OK:
                            AssetIssueModel.objects.filter(issue_id=issue_obj.issue_id).delete()
                            return email_response
                    # -------------------------------------------------

                    # update fields after db entry has been made
                    issue_obj, update_status = IssueUpdater.update_issue_post_creation(issue_obj, user)
                    if update_status.status_code != status.HTTP_202_ACCEPTED:
                        return update_status

                    # create issue record
                    company_name = detailed_user.company.company_name
                    channel_name = company_name
                    pusher_payload = {'location': issue_obj.location.location_id}
                    history_func = IssueHistory.create_issue_record_by_obj
                    pusher_helper = PusherHelper(channel_name, PusherHelper.IssueCreatedEvent, pusher_payload, False, history_func)
                    if(not pusher_helper.push(issue_obj)):
                        Logger.getLogger().error(CustomError.MHF_1)
                        return Response(CustomError.get_full_error_json(CustomError.MHF_1), status=status.HTTP_400_BAD_REQUEST)

                    # create asset event log
                    description = "Issue " + str(issue_obj.custom_id) + " was added."
                    event_log_response = IssueHistory.create_issue_event_log(issue_obj, description)
                    if event_log_response.status_code != status.HTTP_201_CREATED:
                        return event_log_response

                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    AssetIssueModel.objects.filter(issue_id=issue_obj.issue_id).delete()
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
                    return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

            Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, serializer.errors))
            return Response(CustomError.get_full_error_json(CustomError.S_0, serializer.errors), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.I_0, e))
            return Response(CustomError.get_full_error_json(CustomError.I_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
        
    @staticmethod
    def handle_search_issue_by_vin(_vin, user):
        try:
            issues, search_reponse = IssueHelper.get_issues(_vin, user.db_access)
            if search_reponse.status_code != status.HTTP_200_OK:
                return search_reponse
            relevant_issues = IssueHelper.select_related_to_issue(IssueHelper.filter_issues_for_user(issues, user))
            issue_id_list = relevant_issues.values_list('issue_id', flat=True)
            serializer = LightIssueSerializer(relevant_issues, many=True, context=IssueHelper.get_issue_ser_context(issue_id_list, user.db_access))
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.I_0, e))
            return Response(CustomError.get_full_error_json(CustomError.I_0, e), status=status.HTTP_400_BAD_REQUEST)
    
    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_mark_issue_status(_issue_id, _status, user):
        try:
            issue_obj = AssetIssueModel.objects.using(user.db_access).get(pk=_issue_id)

            if not AssetHelper.check_asset_status_active(issue_obj.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            validated_bool = HelperMethods.validate_bool(_status)
            old_status = issue_obj.is_resolved
            issue_obj.is_resolved = validated_bool
            issue_obj.save()

            # set modified_by
            issue_obj, modified_by_status = IssueUpdater.update_issue_modified_by(issue_obj, user)
            if modified_by_status.status_code != status.HTTP_202_ACCEPTED:
                return modified_by_status

            event_name = None
            pusher_payload = {'location': issue_obj.location.location_id}
            # check if a issue that was originally resolved is marked as unresolved
            if issue_obj.is_resolved:
                event_name = PusherHelper.IssueResolvedEvent
            # check if a issue that was originally unresolved is marked as resolved
            else:
                event_name = PusherHelper.IssueUnresolvedEvent
            skip_push = False
            if old_status == issue_obj.is_resolved:
                skip_push = True

            channel_name = DetailedUser.objects.get(email=user.email).company.company_name
            history_func = IssueHistory.create_issue_record_by_obj
            pusher_helper = PusherHelper(channel_name, event_name, pusher_payload, skip_push, history_func)
            # create issue record
            if(not pusher_helper.push(issue_obj)):
                Logger.getLogger().error(CustomError.MHF_4)
                return Response(CustomError.get_full_error_json(CustomError.MHF_4), status=status.HTTP_400_BAD_REQUEST)

            # create asset event log
            description = "Issue " + str(issue_obj.custom_id) + " resolved status was set to " + str(validated_bool) + "."
            event_log_response = IssueHistory.create_issue_event_log(issue_obj, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_set_issue_type(request_data, user):
        try:
            req_id = request_data.get("issue_id")
            req_type = request_data.get("issue_type")
            
            issue_obj = AssetIssueModel.objects.using(user.db_access).get(pk=req_id)

            if not AssetHelper.check_asset_status_active(issue_obj.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            issue_obj.issue_type = req_type
            issue_obj.save()

            # set modified_by
            issue_obj, modified_by_status = IssueUpdater.update_issue_modified_by(issue_obj, user)
            if modified_by_status.status_code != status.HTTP_202_ACCEPTED:
                return modified_by_status

            # create issue record
            if(not IssueHistory.create_issue_record_by_obj(issue_obj)):
                Logger.getLogger().error(CustomError.MHF_4)
                return Response(CustomError.get_full_error_json(CustomError.MHF_4), status=status.HTTP_400_BAD_REQUEST)

            # create asset event log
            description = "Issue " + str(issue_obj.custom_id) + " type was set to " + str(req_type) + "."
            event_log_response = IssueHistory.create_issue_event_log(issue_obj, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_list_filtered_issues(request_data, user):
        try:
            _issue_type = request_data.get("issue_type", None)
            queryset = None

            if _issue_type is not None:
                queryset = IssueHelper.select_related_to_issue(AssetIssueModel.objects.using(user.db_access).filter(issue_type=_issue_type))
            else:
                queryset = IssueHelper.select_related_to_issue(AssetIssueModel.objects.using(user.db_access).all())

            relevant_qs = IssueHelper.filter_issues_for_user(queryset, user)
            issue_id_list = relevant_qs.values_list('issue_id', flat=True)
            ser = LightIssueSerializer(relevant_qs, many=True, context=IssueHelper.get_issue_ser_context(issue_id_list, user.db_access))

            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_critical_issue_count(user):
        try:
            queryset = AssetIssueModel.objects.using(user.db_access).filter(issue_type="Critical")
            count = IssueHelper.filter_issues_for_user(queryset, user).count()
            return Response({"count":count}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_non_critical_issue_count(user):
        try:
            queryset = AssetIssueModel.objects.using(user.db_access).filter(issue_type="Non-Critical")
            count = IssueHelper.filter_issues_for_user(queryset, user).count()
            return Response({"count":count}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_unresolved_issue_count(user):
        try:
            queryset = AssetIssueModel.objects.using(user.db_access).filter(is_resolved=False)
            count = IssueHelper.filter_issues_for_user(queryset, user).count()
            return Response({"count":count}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_resolved_issue_count(user):
        try:
            queryset = AssetIssueModel.objects.using(user.db_access).filter(is_resolved=True)
            count = IssueHelper.filter_issues_for_user(queryset, user).count()
            return Response({"count":count}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_issue_percentage_resolved(user):
        try:
            total_qs = AssetIssueModel.objects.using(user.db_access).all()
            count_total = IssueHelper.filter_issues_for_user(total_qs, user).count()
            resolved_qs = AssetIssueModel.objects.using(user.db_access).filter(is_resolved=True)
            count_resolved = IssueHelper.filter_issues_for_user(resolved_qs, user).count()
            percentageResolved = round(((count_resolved / count_total) * 100), 2)
            return Response({"resolved_percent":percentageResolved}, status=status.HTTP_200_OK)
        except ZeroDivisionError as zde:
            Logger.getLogger().error(zde)
            return Response({"resolved_percent":0}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_issue_by_repair_id(_repair_id, user):
        try:
            issues = IssueHelper.select_related_to_issue(AssetIssueModel.objects.using(user.db_access).filter(repair_id=_repair_id))
            relevant_issues = IssueHelper.filter_issues_for_user(issues, user)
            issue_id_list = relevant_issues.values_list('issue_id', flat=True)
            ser = LightIssueSerializer(relevant_issues, many=True, context=IssueHelper.get_issue_ser_context(issue_id_list, user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_set_issue_accident_id(_issue_id, _accident_id, user):
        try:
            issue_obj = AssetIssueModel.objects.using(user.db_access).get(pk=_issue_id)

            if not AssetHelper.check_asset_status_active(issue_obj.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            issue_obj.accident_id = AccidentModel.objects.using(user.db_access).get(accident_id = _accident_id)
            issue_obj.save()

            # set modified_by
            disposal_request_obj, modified_by_status = IssueUpdater.update_issue_modified_by(issue_obj, user)
            if modified_by_status.status_code != status.HTTP_202_ACCEPTED:
                return modified_by_status

            # create issue record
            if(not IssueHistory.create_issue_record_by_obj(issue_obj)):
                Logger.getLogger().error(CustomError.MHF_4)
                return Response(CustomError.get_full_error_json(CustomError.MHF_4), status=status.HTTP_400_BAD_REQUEST)

            # create asset event log
            description = "Issue " + str(issue_obj.custom_id) + " was linked to accident " + str(issue_obj.accident_id.custom_id) + "."
            event_log_response = IssueHistory.create_issue_event_log(issue_obj, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response

            return Response("Issue (id: " + str(_issue_id) + ") accident_id set to " + str(_accident_id), status=status.HTTP_200_OK)

        except ObjectDoesNotExist as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_unresolved_issues_by_vin(_asset_VIN, user):
        try:
            issues = IssueHelper.select_related_to_issue(AssetIssueModel.objects.using(user.db_access).filter(VIN=_asset_VIN, is_resolved=False))
            relevant_issues = IssueHelper.filter_issues_for_user(issues, user)
            issue_id_list = relevant_issues.values_list('issue_id', flat=True)
            ser = LightIssueSerializer(relevant_issues, many=True, context=IssueHelper.get_issue_ser_context(issue_id_list, user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            Logger.getLogger().error("ObjectDoesNotExist")
            return Response(CustomError.get_full_error_json(CustomError.IDNE_0), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_issue_details_by_id(issue_id, user):
        try:
            issue, issue_response = IssueHelper.get_issue_by_id(issue_id, user.db_access)
            if issue_response.status_code != status.HTTP_302_FOUND:
                return issue_response
            ser = LightIssueSerializer(issue, context=IssueHelper.get_issue_ser_context([issue.issue_id], user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_issue_details_by_custom_id(custom_issue_id, user):
        try:
            issue, issue_response = IssueHelper.get_issue_by_custom_id(custom_issue_id, user.db_access)
            if issue_response.status_code != status.HTTP_302_FOUND:
                return issue_response
            ser = LightIssueSerializer(issue, context=IssueHelper.get_issue_ser_context([issue.issue_id], user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_issue_list(user):
        try:
            issues = IssueHelper.select_related_to_issue(AssetIssueModel.objects.using(user.db_access).all())
            relevant_issues = IssueHelper.filter_issues_for_user(issues, user)
            issue_id_list = relevant_issues.values_list('issue_id', flat=True)
            ser = LightIssueSerializer(relevant_issues,many=True,context=IssueHelper.get_issue_ser_context(issue_id_list, user.db_access))
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_issue(request_data, user):
        try:
            # get issue
            issue, issue_response = IssueHelper.get_issue_by_id(request_data.get("issue_id"), user.db_access)
            if issue_response.status_code != status.HTTP_302_FOUND:
                return issue_response

            if not AssetHelper.check_asset_status_active(issue.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            # update issue
            updated_issue, is_important, update_issue_response = IssueUpdater.update_issue_fields(issue, request_data, user)
            if update_issue_response.status_code != status.HTTP_202_ACCEPTED:
                return update_issue_response

            # create issue record
            if(not IssueHistory.create_issue_record_by_obj(updated_issue)):
                Logger.getLogger().error(CustomError.MHF_4)
                return Response(CustomError.get_full_error_json(CustomError.MHF_4), status=status.HTTP_400_BAD_REQUEST)

            if is_important:
                # -------------- Email issue report ---------------
                notification_config, resp = NotificationHelper.get_notification_config_by_name("New Asset Issue", user.db_access)
                if resp.status_code != status.HTTP_302_FOUND:
                    return resp
                if notification_config.active and (
                    notification_config.triggers is None or (
                        "update_issue" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                    )
                ):
                    file_info, html_message = PdfManager.gen_issue_pdf_report(updated_issue, notification_config, user, is_update=True)
                    email_title = "Issue (ID " + str(updated_issue.issue_id) + ")" + " Has Been Updated - Auto-Generated Email"

                    manager_emails = UserHelper.get_managers_emails_by_location(user.db_access, [IssueHelper.get_issue_location(updated_issue)])
                    if notification_config.recipient_type == "auto":
                        recipients = manager_emails
                    else:
                        recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access)

                    if(file_info is not None):
                        email_response = Email.send_email_notification(recipients, email_title, html_message, [file_info], html_content=True)
                    else:
                        email_response = Email.send_email_notification(recipients, email_title, html_message, [], html_content=True)
                    if email_response.status_code != status.HTTP_200_OK:
                        return email_response

                # if issue is related to a repair --> send update email to the vendor
                if updated_issue.repair_id is not None and RepairHelper.repair_exists_by_id(updated_issue.repair_id.repair_id, user.db_access):
                    # -------------- Email repair report --------------
                    notification_config, resp = NotificationHelper.get_notification_config_by_name("New Repair", user.db_access)
                    if resp.status_code != status.HTTP_302_FOUND:
                        return resp
                    if notification_config.active and (
                    notification_config.triggers is None or (
                        "update_issue" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                        )
                    ):
                        repair_obj, repair_response = RepairHelper.get_repair_request_by_id(updated_issue.repair_id.repair_id, user.db_access)
                        asset_obj = AssetHelper.get_asset_by_VIN(repair_obj.VIN, user.db_access)
                        issues = IssueHelper.get_issue_by_repair_id(repair_obj.repair_id, user.db_access)
                        file_info, html_message, email_title = PdfManager.gen_repair_order_pdf(repair_obj, asset_obj, issues, notification_config, user, is_update=True)
                        if not repair_obj.in_house:
                            if notification_config.recipient_type == "auto":
                                recipients = list(manager_emails) + [str(repair_obj.vendor_email)]
                            else:
                                recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access)

                            if(file_info is not None):
                                email_response = Email.send_email_notification(recipients, email_title, html_message, [file_info], html_content=True)
                            else:
                                email_response = Email.send_email_notification(recipients, email_title, html_message, [], html_content=True)
                            if email_response.status_code != status.HTTP_200_OK:
                                return email_response
                # --------------------------------------------------
            # create asset event log
            description = "Issue " + str(updated_issue.custom_id) + " was updated."
            event_log_response = IssueHistory.create_issue_event_log(updated_issue, description)
            if event_log_response.status_code != status.HTTP_201_CREATED:
                return event_log_response
            updated_issue.save()
            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)