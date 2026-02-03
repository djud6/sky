from os import stat
from rest_framework.response import Response
from rest_framework import status
from django.db.models.query_utils import Q
from ..FileManager.FileInfo import FileInfo
from core.Helper import HelperMethods
import codecs
import pdfkit
from api.Models.Company import Company
from api.Models.asset_model import AssetModel
from api.Models.asset_disposal import AssetDisposalModel
from ..UserManager.UserHelper import UserHelper
from ..JobSpecificationManager.JobSpecificationHelper import JobSpecificationHelper
from ..BusinessUnitManager.BusinessUnitHelper import BusinessUnitHelper
from ..NotificationManager.NotificationHelper import NotificationHelper
from api_vendor.Models.vendor import VendorModel
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging
import traceback

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class PdfManager:

    # Constants
    td_none = '<td style="display: none;">'

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_temp_password_html(password, user_obj):
        # ----------------- Placeholders ----------------
        new_password = "%TEMP_PASSWORD%"
        logo = "%logo%"

        try:

            # ---------- Get templates required to build repair order html string -----------

            temp_password_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/TempPassword.html", 'r', encoding='utf-8-sig')
            temp_password_template_string = temp_password_template_file.read()

            # -------------------------- Get company info from db ---------------------------

            detailed_user = UserHelper.get_detailed_user_obj(user_obj.email, user_obj.db_access)

            # ------------------------------- Insert password -------------------------------
            
            temp_password_template_string = temp_password_template_string.replace(new_password, password)
            temp_password_template_string = temp_password_template_string.replace(logo, str(detailed_user.company.software_logo))

            return temp_password_template_string
        
        # Return nothing because generation of the html string has failed
        except Exception as e:
            Logger.getLogger().error(e)
            return "Failed to generate new account details email. Please contact administrator."

    @staticmethod
    def gen_reset_password_html(url, user_obj):
        # ----------------- Placeholders ----------------
        reset_link = "%RESET_LINK%"
        logo = "%logo%"

        try:

            # ---------- Get templates required to build repair order html string -----------

            reset_password_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/ResetPassword.html", 'r', encoding='utf-8-sig')
            reset_password_template_string = reset_password_template_file.read()

            # -------------------------- Get company info from db ---------------------------

            detailed_user = UserHelper.get_detailed_user_obj(user_obj.email, user_obj.db_access)

            # ------------------------------- Insert password -------------------------------
            
            reset_password_template_string = reset_password_template_string.replace(reset_link, url)
            reset_password_template_string = reset_password_template_string.replace(logo, str(detailed_user.company.software_logo))

            return reset_password_template_string
        
        # Return nothing because generation of the html string has failed
        except Exception as e:
            Logger.getLogger().error(e)
            return "Failed to generate new account details email. Please contact administrator."

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_repair_order_pdf(repair_order_obj, asset_obj, issues_in_repair, config, user_obj, is_update=False):
        
        # ----------------- Placeholders ----------------
        company_name = "%CompanyName%"
        company_address = "%CompanyAddress%"
        company_phone = "%CompanyPhone%"

        asset_num = "%Asset#%"
        serial_num = "%Serial#%"
        license_num = "%License%"
        engine_type = "%EngineType%"
        odometer = "%Odometer%"
        engine_hours = "%EngineHours%"
        make = "%Make%"
        model = "%Model%"

        repair_id = "%repair_id%"
        po_num = "%PO#%"
        wo_num = "%WO#%"
        fleet_contact_email = "%fleet_contact_email%"
        fleet_contact_name = "%fleet_contact_name%"
        vendor_pickup_date = "%VendorPickupDate%"
        est_return_date = "%EstReturnDate%"
        pickup_location = "%PickUpLocation%"
        dropoff_location = "%DropOffLocation%"
        invoice_to = "%InvoiceTo%"

        issue_repair_category = "%IssueRepairCategory%"
        issue_title = "%IssueTitle%"
        issue_description = "%IssueDescription%"

        header = "%HEADER%"
        urgent = "%URGENT%"
        custom_text = "%CUSTOM_TEXT%"
        logo = "%logo%"

        try:

            # ---------- Get templates required to build repair order html string -----------

            repair_order_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/RepairOrderTemplate.html", 'r', encoding='utf-8-sig')
            repair_order_template_string = repair_order_template_file.read()
            issue_row_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/IssueRowTemplate.html", 'r', encoding='utf-8-sig')
            issue_row_template = issue_row_template_file.read()

            # -------------------------- Get company info from db ---------------------------

            detailed_user = UserHelper.get_detailed_user_obj(user_obj.email, user_obj.db_access)
            
            # -------- Insert Company Info, Vehicle Info, and Repair Request Details --------
            
            repair_order_template_string = repair_order_template_string.replace(company_name, str(detailed_user.company.company_name))
            repair_order_template_string = repair_order_template_string.replace(company_address, str(detailed_user.company.company_address))
            repair_order_template_string = repair_order_template_string.replace(company_phone, str(detailed_user.company.company_phone))

            repair_order_template_string = repair_order_template_string.replace(asset_num, str(asset_obj.unit_number))
            repair_order_template_string = repair_order_template_string.replace(serial_num, str(asset_obj.VIN))
            repair_order_template_string = repair_order_template_string.replace(license_num, str(asset_obj.license_plate))
            repair_order_template_string = repair_order_template_string.replace(engine_type, str(asset_obj.engine))
            repair_order_template_string = repair_order_template_string.replace(odometer, str(asset_obj.mileage))
            repair_order_template_string = repair_order_template_string.replace(engine_hours, str(asset_obj.hours))
            repair_order_template_string = repair_order_template_string.replace(make, str(HelperMethods.check_none_type_obj(asset_obj,"equipment_type","manufacturer","name")))
            repair_order_template_string = repair_order_template_string.replace(model, str(HelperMethods.check_none_type_obj(asset_obj,"equipment_type","model_number")))
    
            repair_order_template_string = repair_order_template_string.replace(repair_id, str(repair_order_obj.repair_id))
            repair_order_template_string = repair_order_template_string.replace(po_num, str(repair_order_obj.work_order)[::-1])
            repair_order_template_string = repair_order_template_string.replace(wo_num, str(repair_order_obj.work_order))
            repair_order_template_string = repair_order_template_string.replace(fleet_contact_email, str(user_obj.email))
            repair_order_template_string = repair_order_template_string.replace(fleet_contact_name, str(user_obj.first_name + " " + user_obj.last_name))
            repair_order_template_string = repair_order_template_string.replace(invoice_to, str(HelperMethods.check_none_type_obj(repair_order_obj,"VIN","department","accounting_email")))
            repair_order_template_string = repair_order_template_string.replace(vendor_pickup_date, str(repair_order_obj.available_pickup_date))
            repair_order_template_string = repair_order_template_string.replace(est_return_date, str(repair_order_obj.estimated_delivery_date))
            repair_order_template_string = repair_order_template_string.replace(pickup_location, str(HelperMethods.check_none_type_obj(asset_obj,"current_location","location_name")))
            repair_order_template_string = repair_order_template_string.replace(dropoff_location, str(HelperMethods.check_none_type_obj(asset_obj,"current_location","location_name")))

            repair_order_template_string = repair_order_template_string.replace(logo, str(detailed_user.company.software_logo))

            # ----------------- Insert issues attached to this repair request -----------------

            for issue in issues_in_repair:
                custom_issue = issue_row_template.replace(issue_repair_category, str(issue.issue_result))
                custom_issue = custom_issue.replace(issue_title, str(issue.issue_title))   
                custom_issue = custom_issue.replace(issue_description, str(issue.issue_details))
                repair_order_template_string = repair_order_template_string.replace("<!-- Insert Issue Here -->", custom_issue)

            # -------------------------- Construct title and header --------------------------

            # Construct title and header
            title = "Repair Request " + str(repair_order_obj.work_order)
            if repair_order_obj.is_urgent:
                title = "URGENT " + title
                repair_order_template_string = repair_order_template_string.replace(urgent, "URGENT ")
            else:
                repair_order_template_string = repair_order_template_string.replace(urgent, "")

            if is_update:
                title = title + " Has Been Updated"
                repair_order_template_string = repair_order_template_string.replace(header, "Repair Request Order Has Been Updated")
            else:
                repair_order_template_string = repair_order_template_string.replace(header, "Repair Request Order")

            title = title + " - Auto-Generated Email"

            if config.custom_text is not None:
                repair_order_template_string = repair_order_template_string.replace(custom_text, config.custom_text)

            # ----------------------- Show/Hide fields based on config ------------------------

            if config.custom_text is None:
                start, end = '<!-- CUSTOM_TEXT START -->', '<!-- CUSTOM_TEXT END -->'
                repair_order_template_string = HelperMethods.replace_substring(repair_order_template_string, start, end, PdfManager.td_none)

            config_fields = None
            if config.fields is not None:
                config_fields = NotificationHelper.parse_fields_to_list(config.fields)

            if config_fields is not None:
                
                mutable_fields = [
                    "company_name", "company_address", "company_phone", "company_phone", "asset_num", "serial_num",
                    "license_num", "engine_type", "odometer", "engine_hours", "make", "model", "repair_id", "po_num", "wo_num",
                    "fleet_contact_email", "fleet_contact_name", "vendor_pickup_date", "est_return_date", "est_return_date",
                    "pickup_location", "dropoff_location", "invoice_to", "issue_repair_category", "issue_title", "issue_description"
                ]

                for field in mutable_fields:
                    if field not in config_fields:
                        start, end = '<!-- ' + str(field ) + ' START -->', '<!-- ' + str(field) + ' END -->'
                        repair_order_template_string = HelperMethods.replace_substring(repair_order_template_string, start, end, "")

            # -------------------- Generate pdf from the custom html string -------------------

            try:
                file_info = PdfManager.gen_pdf_from_html_with_pdfkit(str(HelperMethods.GetProjectRoot()) + "\\temp\\" + title + ".pdf", repair_order_template_string)

            # Return the html string but no pdf attachment location
            except Exception as e:
                Logger.getLogger().error(e)
                return None, repair_order_template_string, title

            # Return html string and pdf attachment location
            return file_info, repair_order_template_string, title

        # Return nothing because generation of the html string has failed
        except Exception as e:
            Logger.getLogger().error(e)
            # TODO: What should we print on the email if the html wasn't generated?
            return None, "Failed to generate repair request. Please contact administrator.", title
        
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def gen_issue_pdf_report(issue_obj, config, user, is_update=False):
        
        # ---------------------------- placeholders ------------------------------
        reported_by = "%reported_by%"
        issue_id = "%id%"
        vin = "%vin%"
        issue_type = "%type%"
        cause = "%cause%"
        date_created = "%date_created%"
        date_updated = "%date_updated%"
        status = "%status%"

        issue_repair_category = "%IssueRepairCategory%"
        issue_title = "%IssueTitle%"
        issue_description = "%IssueDescription%"

        header = "%HEADER%"
        custom_text = "%CUSTOM_TEXT%"

        logo = "%logo%"

        try:

            # ---------- Get templates required to build issue html string -----------

            issue_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/IssueTemplate.html", 'r', encoding='utf-8-sig')
            issue_template_string = issue_template_file.read()

            # -------------------------- Get company info from db ---------------------------

            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            # ------------------------------- Add header ------------------------------------

            header_content = "New Issue Reported By %reported_by%"
            if is_update:
                header_content = "Issue Updated By %reported_by%"

            issue_template_string = issue_template_string.replace(header, header_content)

            if config.custom_text is not None:
                issue_template_string = issue_template_string.replace(custom_text, config.custom_text)

            # ---------------- Replace placeholders in issue template ----------------

            issue_status = "Unresolved"
            if(issue_obj.is_resolved):
                issue_status = "Resolved"

            issue_template_string = issue_template_string.replace(reported_by, str(user.email))
            issue_template_string = issue_template_string.replace(issue_id, str(issue_obj.issue_id))
            issue_template_string = issue_template_string.replace(vin, str(issue_obj.VIN))
            issue_template_string = issue_template_string.replace(issue_type, str(issue_obj.issue_type))
            issue_template_string = issue_template_string.replace(cause, str(issue_obj.issue_result))
            issue_template_string = issue_template_string.replace(date_created, str(issue_obj.issue_created))
            issue_template_string = issue_template_string.replace(date_updated, str(issue_obj.issue_updated))
            issue_template_string = issue_template_string.replace(status, str(issue_status))

            issue_template_string = issue_template_string.replace(issue_repair_category, str(issue_obj.issue_result))
            issue_template_string = issue_template_string.replace(issue_title, str(issue_obj.issue_title))
            issue_template_string = issue_template_string.replace(issue_description, str(issue_obj.issue_details))

            issue_template_string = issue_template_string.replace(logo, str(detailed_user.company.software_logo))

            # ----------------------- Show/Hide fields based on config ------------------------

            if config.custom_text is None:
                start = "<!-- CUSTOM_TEXT START -->"
                end = "<!-- CUSTOM_TEXT END -->"
                issue_template_string = HelperMethods.replace_substring(issue_template_string, start, end, PdfManager.td_none)

            config_fields = None
            if config.fields is not None:
                config_fields = NotificationHelper.parse_fields_to_list(config.fields)

            if config_fields is not None:
                
                mutable_fields = [
                    "issue_id", "vin", "issue_type", "cause", "date_created", "date_updated", "status",
                    "issue_repair_category", "issue_title", "issue_description"
                ]

                for field in mutable_fields:
                    if field not in config_fields:
                        start, end = '<!-- ' + str(field ) + ' START -->', '<!-- ' + str(field) + ' END -->'
                        issue_template_string = HelperMethods.replace_substring(issue_template_string, start, end, "")

            # -------------------- Generate pdf from the custom html string -------------------

            try:
                file_info = PdfManager.gen_pdf_from_html_with_pdfkit(str(HelperMethods.GetProjectRoot()) + "\\temp\\IssueReport.pdf", issue_template_string)
            
            # Return the html string but no pdf attachment location
            except Exception as e:
                Logger.getLogger().error(e)
                return None, issue_template_string

            # Return html string and pdf attachment location
            return file_info, issue_template_string

        # Return nothing because generation of the html string has failed
        except Exception as e:
            Logger.getLogger().error(e)
            # TODO: What should we print on the email if the html wasn't generated?
            return None, "Failed to generate issue report. Please contact administrator."

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_accident_pdf_report(accident_obj, config, user, is_update=False):

        # ---------------------------- placeholders ------------------------------
        

        reported_by = "%reported_by%"
        accident_id = "%id%"
        vin = "%vin%"
        is_preventable = "%is_preventable%"
        is_equipment_failure = "%is_equipment_failure%"
        evaluation_required = "%evaluation_required%"
        date_created = "%date_created%"
        date_updated = "%date_updated%"
        is_operational = "%is_operational%"

        header = "%HEADER%"
        custom_text = "%CUSTOM_TEXT%"

        logo = "%logo%"

        try:

            # ---------- Get templates required to build accident html string -----------

            accident_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/AccidentTemplate.html", 'r', encoding='utf-8-sig')
            accident_template_string = accident_template_file.read()

            # -------------------------- Get company info from db ---------------------------

            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            # ------------------------------- Add header ------------------------------------

            header_content = "New Accident Reported By %reported_by%"
            if is_update:
                header_content = "Accident Report Updated By %reported_by%"

            accident_template_string = accident_template_string.replace(header, header_content)

            if config.custom_text is not None:
                accident_template_string = accident_template_string.replace(custom_text, config.custom_text)

            # ---------------- Replace placeholders in accident template ----------------

            accident_preventable = "No"
            if(accident_obj.is_preventable):
                accident_preventable = "Yes"

            accident_equipment_failure = "No"
            if(accident_obj.is_equipment_failure):
                accident_equipment_failure = "Yes"

            accident_evaluation_required = "No"
            if(accident_obj.evaluation_required):
                accident_evaluation_required = "Yes"

            asset_operational = "No"
            if(accident_obj.is_operational):
                asset_operational = "Yes"

            accident_template_string = accident_template_string.replace(accident_id, str(accident_obj.accident_id))
            accident_template_string = accident_template_string.replace(vin, str(accident_obj.VIN))
            accident_template_string = accident_template_string.replace(is_preventable, str(accident_preventable))
            accident_template_string = accident_template_string.replace(is_equipment_failure, str(accident_equipment_failure))
            accident_template_string = accident_template_string.replace(evaluation_required, str(accident_evaluation_required))
            accident_template_string = accident_template_string.replace(date_created, str(accident_obj.date_created))
            accident_template_string = accident_template_string.replace(date_updated, str(accident_obj.date_modified))
            accident_template_string = accident_template_string.replace(is_operational, str(asset_operational))
            accident_template_string = accident_template_string.replace(reported_by, str(user.first_name + " " + user.last_name))

            accident_template_string = accident_template_string.replace(logo, str(detailed_user.company.software_logo))

            # ----------------------- Show/Hide fields based on config ------------------------

            if config.custom_text is None:
                start = "<!-- CUSTOM_TEXT START -->"
                end = "<!-- CUSTOM_TEXT END -->"
                accident_template_string = HelperMethods.replace_substring(accident_template_string, start, end, PdfManager.td_none)

            config_fields = None
            if config.fields is not None:
                config_fields = NotificationHelper.parse_fields_to_list(config.fields)

            if config_fields is not None:
                
                mutable_fields = [
                    "accident_id", "vin", "is_preventable", "is_equipment_failure", "evaluation_required", "date_created",
                    "date_updated", "is_operational"
                ]

                for field in mutable_fields:
                    if field not in config_fields:
                        start, end = '<!-- ' + str(field ) + ' START -->', '<!-- ' + str(field) + ' END -->'
                        accident_template_string = HelperMethods.replace_substring(accident_template_string, start, end, "")
                
            # -------------------- Generate pdf from the custom html string -------------------

            try:
                file_info = PdfManager.gen_pdf_from_html_with_pdfkit(str(HelperMethods.GetProjectRoot()) + "\\temp\\AccidentReport.pdf", accident_template_string)
            
            # Return the html string but no pdf attachment location
            except Exception as e:
                print(e)
                Logger.getLogger().error(e)
                return None, accident_template_string

            # Return html string and pdf attachment location
            return file_info, accident_template_string

        # Return nothing because generation of the html string has failed
        except Exception as e:
            Logger.getLogger().error(e)
            # TODO: What should we print on the email if the html wasn't generated?
            return None, "Failed to generate accident report. Please contact administrator."

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_maintenance_pdf_request(maintenance_requests, config, user, is_update=False):

        # ---------------------------- placeholders ------------------------------
        
        plural = "%plural%"
        
        maintenance_id = "%id%"
        vin = "%vin%"
        inspection_type = "%inspection_type%"
        location = "%location%"
        mileage = "%mileage%"
        hours = "%hours%"
        assigned_vendor = "%assigned_vendor%"
        fleet_contact_email = "%fleet_contact_email%"
        fleet_contact_name = "%fleet_contact_name%"
        requested_delivery = "%requested_delivery%"
        estimated_delivery = "%estimated_delivery%"
        status = "%status%"

        header = "%HEADER%"
        custom_text = "%CUSTOM_TEXT%"

        logo = "%logo%"

        try:
            # ---------- Get templates required to build maintenance html string -----------

            maintenance_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/MaintenanceRequestTemplate.html", 'r', encoding='utf-8-sig')
            maintenance_template_string = maintenance_template_file.read()
            maintenance_row_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/MaintenanceRequestRowTemplate.html", 'r', encoding='utf-8-sig')
            maintenance_row_template_string = maintenance_row_template_file.read()

            # -------------------------- Get company info from db ---------------------------

            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            # ------------------------------- Add header ------------------------------------

            header_content = "New Maintenance Request%plural%"
            if is_update:
                header_content = "Maintenance Request Has Been Updated"

            maintenance_template_string = maintenance_template_string.replace(header, header_content)

            if config.custom_text is not None:
                maintenance_template_string = maintenance_template_string.replace(custom_text, config.custom_text)

            # ---------------- Replace placeholders in maintenance template ----------------

            if(len(maintenance_requests) > 1):
                maintenance_template_string = maintenance_template_string.replace(plural, "s")
            else:
                maintenance_template_string = maintenance_template_string.replace(plural, "")

            for maint_req in maintenance_requests:

                request_information_string = maintenance_row_template_string.replace(maintenance_id, str(maint_req.maintenance_id))
                request_information_string = request_information_string.replace(vin, str(maint_req.VIN))
                request_information_string = request_information_string.replace(inspection_type, str(maint_req.inspection_type))
                request_information_string = request_information_string.replace(location, str(maint_req.location))
                request_information_string = request_information_string.replace(mileage, str(maint_req.mileage))
                request_information_string = request_information_string.replace(hours, str(maint_req.hours))
                request_information_string = request_information_string.replace(assigned_vendor, str(maint_req.assigned_vendor))
                request_information_string = request_information_string.replace(fleet_contact_email, str(user.email))
                request_information_string = request_information_string.replace(fleet_contact_name, str(user.first_name + " " + user.last_name))
                request_information_string = request_information_string.replace(requested_delivery, str(maint_req.requested_delivery_date))
                request_information_string = request_information_string.replace(estimated_delivery, str(maint_req.estimated_delivery_date))
                request_information_string = request_information_string.replace(status, str(maint_req.status))

                maintenance_template_string = maintenance_template_string.replace("<!-- Insert Maintenance Request Here -->", request_information_string)
                maintenance_template_string = maintenance_template_string.replace(logo, str(detailed_user.company.software_logo))


            # ----------------------- Show/Hide fields based on config ------------------------

            if config.custom_text is None:
                start = "<!-- CUSTOM_TEXT START -->"
                end = "<!-- CUSTOM_TEXT END -->"
                maintenance_template_string = HelperMethods.replace_substring(maintenance_template_string, start, end, PdfManager.td_none)

            config_fields = None
            if config.fields is not None:
                config_fields = NotificationHelper.parse_fields_to_list(config.fields)

            if config_fields is not None:
                
                mutable_fields = [
                    "maintenance_id", "vin", "inspection_type", "location", "mileage", "hours", "assigned_vendor",
                    "fleet_contact_email", "fleet_contact_name", "requested_delivery", "estimated_delivery", "status"
                ]

                for field in mutable_fields:
                    if field not in config_fields:
                        start, end = '<!-- ' + str(field ) + ' START -->', '<!-- ' + str(field) + ' END -->'
                        maintenance_template_string = HelperMethods.replace_substring(maintenance_template_string, start, end, "")

            # -------------------- Generate pdf from the custom html string -------------------
            try:
                file_info = PdfManager.gen_pdf_from_html_with_pdfkit(str(HelperMethods.GetProjectRoot()) + "\\temp\\MaintenanceRequest.pdf", maintenance_template_string)
            
            # Return the html string but no pdf attachment location
            except Exception as e:
                print(e)
                Logger.getLogger().error(e)
                return None, maintenance_template_string

            # Return html string and pdf attachment location
            return file_info, maintenance_template_string

        # Return nothing because generation of the html string has failed
        except Exception as e:
            Logger.getLogger().error(e)
            # TODO: What should we print on the email if the html wasn't generated?
            return None, "Failed to generate maintenance request. Please contact administrator."

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_asset_request_pdf_report(asset_request_obj, config, user, is_update=False, is_cancel=False):
    
        # ---------------------------- placeholders ------------------------------

        vendor_name = "%vendor_name%"
        request_id = "%id%"
        business_unit = "%business_unit%"
        equipment = "%equipment%"
        created_by = "%created_by%"
        date_created = "%date_created%"
        modified_by = "%modified_by%"
        date_required = "%date_required%"
        date_updated = "%date_updated%"
        justification = "%justification%"
        nonstandard_description = "%nonstandard_description%"
        vendor_email = "%vendor_email%"
        fleet_contact = "%fleet_contact%"
        fleet_contact_name = "%fleet_contact_name%"
        status = "%status%"
        user_name_first = "%user_name_first%"
        user_name_last = "%user_name_last%"

        header = "%HEADER%"
        custom_text = "%CUSTOM_TEXT%"

        logo = "%logo%"

        try:

            # ---------- Get templates required to build asset request html string -----------
            
            vendor = VendorModel.vendor_name

            asset_request_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/AssetRequestTemplate.html", 'r', encoding='utf-8-sig')
            asset_request_template_string = asset_request_template_file.read()

            # -------------------------- Get company info from db ---------------------------

            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            # ------------------------------- Add header ------------------------------------

            header_content = "We kindly request a detailed quote that matches the data table below:"
            if is_update:
                header_content = "This asset request has been updated. We kindly request a detailed quote that matches the modified table below:"
            if is_cancel:
                header_content = "The following asset request has been cancelled:"

            asset_request_template_string = asset_request_template_string.replace(header, header_content)

            if config.custom_text is not None:
                asset_request_template_string = asset_request_template_string.replace(custom_text, config.custom_text)

            # ---------------- Replace placeholders in asset request template ----------------

            asset_request_template_string = asset_request_template_string.replace(vendor_name, str(vendor))
            asset_request_template_string = asset_request_template_string.replace(request_id, str(asset_request_obj.id))
            asset_request_template_string = asset_request_template_string.replace(business_unit, str(asset_request_obj.business_unit))
            asset_request_template_string = asset_request_template_string.replace(equipment, str(asset_request_obj.equipment))
            asset_request_template_string = asset_request_template_string.replace(created_by, str(asset_request_obj.created_by))
            asset_request_template_string = asset_request_template_string.replace(date_created, str(asset_request_obj.date_created.date()))
            asset_request_template_string = asset_request_template_string.replace(modified_by, str(asset_request_obj.modified_by))
            asset_request_template_string = asset_request_template_string.replace(date_required, str(asset_request_obj.date_required.date()))
            asset_request_template_string = asset_request_template_string.replace(date_updated, str(asset_request_obj.date_updated.date()))
            asset_request_template_string = asset_request_template_string.replace(justification, str(asset_request_obj.justification))
            asset_request_template_string = asset_request_template_string.replace(nonstandard_description, str(asset_request_obj.nonstandard_description))
            asset_request_template_string = asset_request_template_string.replace(vendor_email, str(asset_request_obj.vendor_email))
            asset_request_template_string = asset_request_template_string.replace(fleet_contact, str(user.email))
            asset_request_template_string = asset_request_template_string.replace(fleet_contact_name, str(user.first_name + " " + user.last_name))
            asset_request_template_string = asset_request_template_string.replace(status, str(asset_request_obj.status))
            asset_request_template_string = asset_request_template_string.replace(user_name_first, str(user.first_name))
            asset_request_template_string = asset_request_template_string.replace(user_name_last, str(user.last_name))

            asset_request_template_string = asset_request_template_string.replace(logo, str(detailed_user.company.software_logo))

            # ----------------------- Show/Hide fields based on config ------------------------

            if config.custom_text is None:
                start = "<!-- CUSTOM_TEXT START -->"
                end = "<!-- CUSTOM_TEXT END -->"
                asset_request_template_string = HelperMethods.replace_substring(asset_request_template_string, start, end, PdfManager.td_none)

            config_fields = None
            if config.fields is not None:
                config_fields = NotificationHelper.parse_fields_to_list(config.fields)

            if config_fields is not None:
                
                mutable_fields = [
                    "request_id", "business_unit", "equipment", "created_by", "date_created", "modified_by",
                    "date_required", "date_updated", "justification", "nonstandard_description", "vendor_email", "fleet_contact",
                    "fleet_contact_name", "status", "user_name_first", "user_name_last"
                ]

                for field in mutable_fields:
                    if field not in config_fields:
                        start, end = '<!-- ' + str(field ) + ' START -->', '<!-- ' + str(field) + ' END -->'
                        asset_request_template_string = HelperMethods.replace_substring(asset_request_template_string, start, end, "")

            # -------------------- Generate pdf from the custom html string -------------------
            try:
                file_info = PdfManager.gen_pdf_from_html_with_pdfkit(str(HelperMethods.GetProjectRoot()) + "\\temp\\AssetRequestReport.pdf", asset_request_template_string)
            
            # Return the html string but no pdf attachment location
            except Exception as e:
                print(e)
                Logger.getLogger().error(e)
                return None, asset_request_template_string

            # Return html string and pdf attachment location
            return file_info, asset_request_template_string

        # Return nothing because generation of the html string has failed
        except Exception as e:
            Logger.getLogger().error(e)
            return None, "Failed to generate asset request report. Please contact administrator."


    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_transfer_pdf_report(transfer_request_obj, config, user, is_update=False):
         # ---------------------------- placeholders ------------------------------

        asset_transfer_id = "%id%"
        vin = "%vin%"
        pickup_date = "%pickup_date%"
        fleet_contact_email = "%fleet_contact_email%"
        fleet_contact_name = "%fleet_contact_name%"
        destination_location = "%destination_location%"
        justification = "%justification%"
        status = "%status%"

        header = "%HEADER%"
        custom_text = "%CUSTOM_TEXT%"

        logo = "%logo%"

        try:

            # ---------- Get templates required to build asset request html string -----------
            
            transfer_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/TransferTemplate.html", 'r', encoding='utf-8-sig')
            transfer_template_string = transfer_template_file.read()

            # -------------------------- Get company info from db ---------------------------

            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            # ------------------------------- Add header ------------------------------------
            header_content = "New Transfer Request ID %id%"
            if is_update:
                header_content = "Transfer Request ID %id% Has Been Updated"

            transfer_template_string = transfer_template_string.replace(header, header_content)

            if config.custom_text is not None:
                transfer_template_string = transfer_template_string.replace(custom_text, config.custom_text)

            # ---------------- Replace placeholders in asset request template ----------------

            transfer_template_string = transfer_template_string.replace(asset_transfer_id, str(transfer_request_obj.asset_transfer_id))
            transfer_template_string = transfer_template_string.replace(vin, str(transfer_request_obj.VIN))
            transfer_template_string = transfer_template_string.replace(fleet_contact_email, str(user.email))
            transfer_template_string = transfer_template_string.replace(fleet_contact_name, str(user.first_name + " " + user.last_name))
            transfer_template_string = transfer_template_string.replace(pickup_date, str(transfer_request_obj.pickup_date))
            transfer_template_string = transfer_template_string.replace(destination_location, str(transfer_request_obj.destination_location))
            transfer_template_string = transfer_template_string.replace(justification, str(transfer_request_obj.justification))
            transfer_template_string = transfer_template_string.replace(status, str(transfer_request_obj.status))

            transfer_template_string = transfer_template_string.replace(logo, str(detailed_user.company.software_logo))

            # ----------------------- Show/Hide fields based on config ------------------------

            if config.custom_text is None:
                start = "<!-- CUSTOM_TEXT START -->"
                end = "<!-- CUSTOM_TEXT END -->"
                transfer_template_string = HelperMethods.replace_substring(transfer_template_string, start, end, PdfManager.td_none)

            config_fields = None
            if config.fields is not None:
                config_fields = NotificationHelper.parse_fields_to_list(config.fields)

            if config_fields is not None:
                
                mutable_fields = [
                    "asset_transfer_id", "vin", "fleet_contact_email", "fleet_contact_name", "pickup_date", "destination_location",
                    "justification", "status"
                ]

                for field in mutable_fields:
                    if field not in config_fields:
                        start, end = '<!-- ' + str(field ) + ' START -->', '<!-- ' + str(field) + ' END -->'
                        transfer_template_string = HelperMethods.replace_substring(transfer_template_string, start, end, "")

            # -------------------- Generate pdf from the custom html string -------------------
            try:
                file_info = PdfManager.gen_pdf_from_html_with_pdfkit(str(HelperMethods.GetProjectRoot()) + "\\temp\\TransferTemplate.pdf", transfer_template_string)
            
            # Return the html string but no pdf attachment location
            except Exception as e:
                print(e)
                Logger.getLogger().error(e)
                return None, transfer_template_string

            # Return html string and pdf attachment location
            return file_info, transfer_template_string

        # Return nothing because generation of the html string has failed
        except Exception as e:
            Logger.getLogger().error(e)
            return None, "Failed to generate asset transfer report. Please contact administrator."

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def gen_auction_disposal_report(disposal_obj, company_obj, config, user, is_update=False):
        try:
            disposal_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/AuctionTemplate.html", 'r', encoding='utf-8-sig')
            disposal_template_string = disposal_template_file.read()

            return PdfManager.gen_generic_disposal_report(disposal_template_string, disposal_obj, company_obj, config, user, is_update=is_update)
        except Exception as e:
            Logger.getLogger().error(e)
            return "Failed to generate asset disposal report. Please contact administrator."

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_donate_disposal_report(disposal_obj, company_obj, config, user, is_update=False):
        try:
            disposal_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/DonationTemplate.html", 'r', encoding='utf-8-sig')
            disposal_template_string = disposal_template_file.read()

            return PdfManager.gen_generic_disposal_report(disposal_template_string, disposal_obj, company_obj, config, user, is_update=is_update)
        except Exception as e:
            Logger.getLogger().error(e)
            return "Failed to generate asset disposal report. Please contact administrator."

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_scrap_disposal_report(disposal_obj, company_obj, config, user, is_update=False):
        try:
            disposal_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/ScrapTemplate.html", 'r', encoding='utf-8-sig')
            disposal_template_string = disposal_template_file.read()

            return PdfManager.gen_generic_disposal_report(disposal_template_string, disposal_obj, company_obj, config, user, is_update=is_update)
        except Exception as e:
            Logger.getLogger().error(e)
            return "Failed to generate asset disposal report. Please contact administrator."

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_generic_disposal_report(disposal_template_string, disposal_obj, company_obj, config, user, is_update):
         # ---------------------------- placeholders ------------------------------

        contact_name = "%contact_name%"
        company = "%company%"
        company_address = "%company_address%"
        contact_email = "%contact_email%"
        date = "%date%"
        available_pickup_date = "%available_pick_up_date%"
        vin = "%VIN%"
        asset_type = "%asset_type%"
        year = "%year%"
        make = "%make%"
        model = "%model%"
        colour = "%colour%"
        odometer = "%odometer%"
        engine_hours = "%engine_hours%"
        location = "%location%"
        manager_contact_email = "%manager_contact_email%"
        interior_condition = "%interior_condition%"
        interior_condition_details = "%interior_condition_details%"
        exterior_condition = "%exterior_condition%"
        exterior_condition_details = "%exterior_condition_details%"
        accident = "%accident%"
        equipment_failure = "%equipment_failure%"

        custom_text = "%CUSTOM_TEXT%"

        logo = "%logo%"

        try:
            # -------------------------- Get company info from db ---------------------------

            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            # ------------------------------- Add header ------------------------------------

            if config.custom_text is not None:
                disposal_template_string = disposal_template_string.replace(custom_text, config.custom_text)

            # ---------------- Replace placeholders in asset request template ----------------

            disposal_template_string = disposal_template_string.replace(contact_name, str(user.first_name + " " + user.last_name)) 
            disposal_template_string = disposal_template_string.replace(company, str(company_obj)) 
            disposal_template_string = disposal_template_string.replace(company_address, str(company_obj.company_address)) 
            disposal_template_string = disposal_template_string.replace(contact_email, str(user.email))
            disposal_template_string = disposal_template_string.replace(date, str(disposal_obj.date_modified)) 
            disposal_template_string = disposal_template_string.replace(vin, str(disposal_obj.VIN))
            disposal_template_string = disposal_template_string.replace(available_pickup_date, str(disposal_obj.available_pickup_date))
            disposal_template_string = disposal_template_string.replace(asset_type, str(HelperMethods.check_none_type_obj(disposal_obj,"VIN","equipment_type")))
            disposal_template_string = disposal_template_string.replace(year, str(HelperMethods.check_none_type_obj(disposal_obj,"VIN","date_of_manufacture","year")))
            disposal_template_string = disposal_template_string.replace(make, str(HelperMethods.check_none_type_obj(disposal_obj,"VIN","equipment_type","manufacturer","name")))
            disposal_template_string = disposal_template_string.replace(model, str(HelperMethods.check_none_type_obj(disposal_obj,"VIN","equipment_type","model_number"))) 
            
            disposal_template_string = disposal_template_string.replace(colour, str(disposal_obj.VIN.colour))

            if HelperMethods.check_none_type_obj(disposal_obj,"VIN","hours_or_mileage") == AssetModel.Mileage or HelperMethods.check_none_type_obj(disposal_obj,"VIN","hours_or_mileage") == AssetModel.Both:
                if disposal_obj.VIN.mileage == -1:
                    disposal_template_string = disposal_template_string.replace(odometer, "NA")
                else:
                    disposal_template_string = disposal_template_string.replace(odometer, str(disposal_obj.VIN.mileage))
            else:
                disposal_template_string = disposal_template_string.replace(odometer, "NA")

            if HelperMethods.check_none_type_obj(disposal_obj,"VIN","hours_or_mileage") == AssetModel.Hours or HelperMethods.check_none_type_obj(disposal_obj,"VIN","hours_or_mileage") == AssetModel.Both:
                if disposal_obj.VIN.hours == -1:
                    disposal_template_string = disposal_template_string.replace(engine_hours, "NA")
                else:
                    disposal_template_string = disposal_template_string.replace(engine_hours, str(disposal_obj.VIN.hours))
            else:
                disposal_template_string = disposal_template_string.replace(engine_hours, "NA")
            
            disposal_template_string = disposal_template_string.replace(location, str(HelperMethods.check_none_type_obj(disposal_obj,"VIN","current_location")))
            disposal_template_string = disposal_template_string.replace(manager_contact_email, str(disposal_obj.created_by))
            disposal_template_string = disposal_template_string.replace(interior_condition, str(disposal_obj.interior_condition))
            disposal_template_string = disposal_template_string.replace(interior_condition_details, str(disposal_obj.interior_condition_details))
            disposal_template_string = disposal_template_string.replace(exterior_condition, str(disposal_obj.exterior_condition))
            disposal_template_string = disposal_template_string.replace(exterior_condition_details, str(disposal_obj.exterior_condition_details))

            if disposal_obj.replacement_reason == AssetDisposalModel.accident:
                disposal_template_string = disposal_template_string.replace(accident, "Yes")
            else:
                disposal_template_string = disposal_template_string.replace(accident, "No")

            if disposal_obj.replacement_reason == AssetDisposalModel.equipment_failure:
                disposal_template_string = disposal_template_string.replace(equipment_failure, "Yes")
            else:
                disposal_template_string = disposal_template_string.replace(equipment_failure, "No")

            disposal_template_string = disposal_template_string.replace(logo, str(detailed_user.company.software_logo))

            # ----------------------- Show/Hide fields based on config ------------------------

            if config.custom_text is None:
                start = "<!-- CUSTOM_TEXT START -->"
                end = "<!-- CUSTOM_TEXT END -->"
                disposal_template_string = HelperMethods.replace_substring(disposal_template_string, start, end, PdfManager.td_none)

            config_fields = None
            if config.fields is not None:
                config_fields = NotificationHelper.parse_fields_to_list(config.fields)

            if config_fields is not None:
                
                mutable_fields = [
                    "contact_name", "company", "company_address", "contact_email", "date", "vin", "available_pickup_date",
                    "asset_type", "year", "make", "model", "colour", "odometer", "engine_hours", "location", "manager_contact_email",
                    "interior_condition", "interior_condition_details", "exterior_condition", "exterior_condition_details",
                    "accident", "equipment_failure"
                ]

                for field in mutable_fields:
                    if field not in config_fields:
                        start, end = '<!-- ' + str(field ) + ' START -->', '<!-- ' + str(field) + ' END -->'
                        disposal_template_string = HelperMethods.replace_substring(disposal_template_string, start, end, "")

            # Return html string and pdf attachment location
            return disposal_template_string
        # Return nothing because generation of the html string has failed
        except Exception as e:
            Logger.getLogger().error(e)
            return "Failed to generate asset disposal report. Please contact administrator."

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_reassign_asset_html(original_asset_obj, updated_asset_dict, config, user):

        vin = "%VIN%"
        old_job_specification = "%old_job_specification%"
        new_job_specification = "%new_job_specification%"
        old_business_unit = "%old_business_unit%"
        new_business_unit = "%new_business_unit%"

        custom_text = "%CUSTOM_TEXT%"

        logo = "%logo%"

        try:
            # ---------- Get templates required to build asset reassignment string --------------
                
            new_asset_reassign_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/AssetReassignTemplate.html", 'r', encoding='utf-8-sig')
            new_asset_reassign_template_string = new_asset_reassign_template_file.read()

            # -------------------------- Get company info from db ---------------------------

            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            # ------------------------------- Add header ------------------------------------

            if config.custom_text is not None:
                new_asset_reassign_template_string = new_asset_reassign_template_string.replace(custom_text, config.custom_text)

            # ------------ Replace placeholders in new asset reassignment template --------------
    
            new_job_spec_obj, response = JobSpecificationHelper.get_job_specification_by_id(updated_asset_dict.get("job_specification"), user.db_access)
            new_business_unit_obj, response = BusinessUnitHelper.get_business_unit_by_id(updated_asset_dict.get("department"), user.db_access)
            new_asset_reassign_template_string = new_asset_reassign_template_string.replace(vin, str(original_asset_obj.VIN))
            new_asset_reassign_template_string = new_asset_reassign_template_string.replace(old_job_specification, str(HelperMethods.check_none_type_obj(original_asset_obj,"job_specification","name")))
            new_asset_reassign_template_string = new_asset_reassign_template_string.replace(new_job_specification, str(new_job_spec_obj.name))
            new_asset_reassign_template_string = new_asset_reassign_template_string.replace(old_business_unit, str(HelperMethods.check_none_type_obj(original_asset_obj,"department","name")))
            new_asset_reassign_template_string = new_asset_reassign_template_string.replace(new_business_unit, str(new_business_unit_obj.name))

            new_asset_reassign_template_string = new_asset_reassign_template_string.replace(logo, str(detailed_user.company.software_logo))

            # ----------------------- Show/Hide fields based on config ------------------------

            if config.custom_text is None:
                start = "<!-- CUSTOM_TEXT START -->"
                end = "<!-- CUSTOM_TEXT END -->"
                new_asset_reassign_template_string = HelperMethods.replace_substring(new_asset_reassign_template_string, start, end, PdfManager.td_none)

            config_fields = None
            if config.fields is not None:
                config_fields = NotificationHelper.parse_fields_to_list(config.fields)

            if config_fields is not None:
                
                mutable_fields = [
                    "vin", "old_job_specification", "new_job_specification", "old_business_unit", "new_business_unit"
                ]

                for field in mutable_fields:
                    if field not in config_fields:
                        start, end = '<!-- ' + str(field ) + ' START -->', '<!-- ' + str(field) + ' END -->'
                        new_asset_reassign_template_string = HelperMethods.replace_substring(new_asset_reassign_template_string, start, end, "")

            return new_asset_reassign_template_string

        # Return nothing because generation of the html string has failed
        except Exception as e:
            Logger.getLogger().error(e)
            return "Failed to generate asset reassignment notification email. Please contact administrator."


    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_new_account_html(user, user_password):

        system = "%system%"
        name = "%name%"
        role = "%role%"
        username = "%username%"
        password = "%password%"

        logo = "%logo%"

        try:

            # ---------- Get templates required to build new account html string -----------
                
            new_account_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/NewAccountTemplate.html", 'r', encoding='utf-8-sig')
            new_account_template_string = new_account_template_file.read()

            # ---------------- Replace placeholders in new account details template ----------------

            user_role = UserHelper.get_role_by_email(user.email, user.db_access)
            full_name = str(user.first_name) + " " + str(user.last_name)
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            new_account_template_string = new_account_template_string.replace(system, str(detailed_user.company.software_name).capitalize())
            new_account_template_string = new_account_template_string.replace(name, str(full_name))
            new_account_template_string = new_account_template_string.replace(role, str(user_role).capitalize())
            new_account_template_string = new_account_template_string.replace(username, str(user.username))
            new_account_template_string = new_account_template_string.replace(password, str(user_password))
            new_account_template_string = new_account_template_string.replace(logo, str(detailed_user.company.software_logo))

            return new_account_template_string

        # Return nothing because generation of the html string has failed
        except Exception as e:
            Logger.getLogger().error(e)
            return "Failed to generate new account details email. Please contact administrator."


    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_error_report_html(error_report_obj, user):

        error_report_id = "%id%"
        title = "%title%"
        type = "%type%"
        description = "%description%"
        steps_to_reproduce = "%steps_to_reproduce%"

        logo = "%logo%"

        try:

            # ---------- Get templates required to build new error report html string ------------
                
            user_feedback_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/UserFeedbackTemplate.html", 'r', encoding='utf-8-sig')
            user_feedback_template_string = user_feedback_template_file.read()

            # -------------------------- Get company info from db ---------------------------

            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            # ---------------- Replace placeholders in user error report template ----------------

            steps = error_report_obj.steps_to_reproduce
            if steps is None:
                steps = ""

            user_feedback_template_string = user_feedback_template_string.replace(error_report_id, str(error_report_obj.error_report_id))
            user_feedback_template_string = user_feedback_template_string.replace(title, str(error_report_obj.error_title))
            user_feedback_template_string = user_feedback_template_string.replace(type, str(error_report_obj.issue_type))
            user_feedback_template_string = user_feedback_template_string.replace(description, str(error_report_obj.error_description))
            user_feedback_template_string = user_feedback_template_string.replace(steps_to_reproduce, str(error_report_obj.steps_to_reproduce))

            user_feedback_template_string = user_feedback_template_string.replace(logo, str(detailed_user.company.software_logo))

            return user_feedback_template_string

        # Return nothing because generation of the html string has failed
        except Exception as e:
            Logger.getLogger().error(e)
            return "Failed to generate user feedback email. Please contact administrator."


    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_daily_maintenance_notification_email(start, end, rule_list, config, db_name, maintenance_forecast_template_string="NA", row_template_string="NA"):
        start_date = "%start_date%"
        end_date = "%end_date%"
        vin = "%VIN%"
        inspection_type = "%inspection_type%"
        row_insert_string = "<!-- Insert Maintenance Forecast Notification Here -->"

        custom_text = "%CUSTOM_TEXT%"

        logo = "%logo%"

        try:
            # ---------- Get templates required to build maintenance forecast html string ------------

            if maintenance_forecast_template_string == "NA":
                maintenance_forecast_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/MaintenanceForecastNotificationTemplate.html", 'r', encoding='utf-8-sig')
                maintenance_forecast_template_string = maintenance_forecast_template_file.read()
            if row_template_string == "NA":
                row_template = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/MaintenanceForecastNotificationRowTemplate.html", 'r', encoding='utf-8-sig')
                row_template_string = row_template.read()

            # -------------------------- Get company info from db ---------------------------

            software_logo = list(Company.objects.using(db_name).all().values_list('software_logo', flat=True))[0]

            # ------------------------------- Add header ------------------------------------

            if config.custom_text is not None:
                maintenance_forecast_template_string = maintenance_forecast_template_string.replace(custom_text, config.custom_text)

            # ---------------- Replace placeholders in maintenance forecast template ----------------

            maintenance_forecast_template_string = maintenance_forecast_template_string.replace(start_date, str(start))
            maintenance_forecast_template_string = maintenance_forecast_template_string.replace(end_date, str(end))
            maintenance_forecast_template_string = maintenance_forecast_template_string.replace(logo, software_logo)

            for rule in rule_list:
                rule_vin = rule[0]
                rule_inspection_name = rule[1]
                cur_row_template_string = row_template_string.replace(vin, str(rule_vin))
                cur_row_template_string = cur_row_template_string.replace(inspection_type, str(rule_inspection_name))
                maintenance_forecast_template_string = maintenance_forecast_template_string.replace(row_insert_string, cur_row_template_string)

            # ----------------------- Show/Hide fields based on config ------------------------

            if config.custom_text is None:
                start = "<!-- CUSTOM_TEXT START -->"
                end = "<!-- CUSTOM_TEXT END -->"
                maintenance_forecast_template_string = HelperMethods.replace_substring(maintenance_forecast_template_string, start, end, PdfManager.td_none)

            config_fields = None
            if config.fields is not None:
                config_fields = NotificationHelper.parse_fields_to_list(config.fields)

            if config_fields is not None:
                
                mutable_fields = [
                    "vin", "inspection_type"
                ]

                for field in mutable_fields:
                    if field not in config_fields:
                        start, end = '<!-- ' + str(field ) + ' START -->', '<!-- ' + str(field) + ' END -->'
                        maintenance_forecast_template_string = HelperMethods.replace_substring(maintenance_forecast_template_string, start, end, "")

            return maintenance_forecast_template_string

        except Exception as e:
            Logger.getLogger().error(e)
            return "Failed to generate maintenance forecast email. Please contact administrator."

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_daily_maintenance_overdue_notification_email(rule_list, config, db_name, maintenance_forecast_template_string="NA", row_template_string="NA"):
        vin = "%VIN%"
        inspection_type = "%inspection_type%"
        row_insert_string = "<!-- Insert Maintenance Forecast Notification Here -->"

        custom_text = "%CUSTOM_TEXT%"

        logo = "%logo%"

        try:
            # ---------- Get templates required to build maintenance forecast html string ------------

            if maintenance_forecast_template_string == "NA":
                maintenance_forecast_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/MaintenanceForecastOverdueTemplate.html", 'r', encoding='utf-8-sig')
                maintenance_forecast_template_string = maintenance_forecast_template_file.read()
            if row_template_string == "NA":
                row_template = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/MaintenanceForecastOverdueRowTemplate.html", 'r', encoding='utf-8-sig')
                row_template_string = row_template.read()

            # -------------------------- Get company info from db ---------------------------

            software_logo = list(Company.objects.using(db_name).all().values_list('software_logo', flat=True))[0]

            # ------------------------------- Add header ------------------------------------

            if config.custom_text is not None:
                maintenance_forecast_template_string = maintenance_forecast_template_string.replace(custom_text, config.custom_text)

            # ---------------- Replace placeholders in maintenance forecast template ----------------

            maintenance_forecast_template_string = maintenance_forecast_template_string.replace(logo, software_logo)

            for rule in rule_list:
                rule_vin = rule[0]
                rule_inspection_name = rule[1]
                cur_row_template_string = row_template_string.replace(vin, str(rule_vin))
                cur_row_template_string = cur_row_template_string.replace(inspection_type, str(rule_inspection_name))
                maintenance_forecast_template_string = maintenance_forecast_template_string.replace(row_insert_string, cur_row_template_string)

            # ----------------------- Show/Hide fields based on config ------------------------

            if config.custom_text is None:
                start = "<!-- CUSTOM_TEXT START -->"
                end = "<!-- CUSTOM_TEXT END -->"
                maintenance_forecast_template_string = HelperMethods.replace_substring(maintenance_forecast_template_string, start, end, PdfManager.td_none)

            config_fields = None
            if config.fields is not None:
                config_fields = PdfManager.parse_field_list(config.fields)

            if config_fields is not None:
                
                mutable_fields = [
                    "vin", "inspection_type"
                ]

                for field in mutable_fields:
                    if field not in config_fields:
                        start, end = '<!-- ' + str(field ) + ' START -->', '<!-- ' + str(field) + ' END -->'
                        maintenance_forecast_template_string = HelperMethods.replace_substring(maintenance_forecast_template_string, start, end, "")

            return maintenance_forecast_template_string

        except Exception as e:
            Logger.getLogger().error(e)
            return "Failed to generate maintenance forecast email. Please contact administrator."

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_expiry_notification_email(start, end, expiry_dict, config, db_name, expiry_notification_template_string="NA", row_template_string="NA"):
        start_date = "%start_date%"
        end_date = "%end_date%"
        vin = "%VIN%"
        expiring_items = "%expiring_items%"
        row_insert_string = "<!-- Insert Expiry Notification Here -->"

        custom_text = "%CUSTOM_TEXT%"

        logo = "%logo%"

        try:
            # ---------- Get templates required to build expiry notification html string ------------

            if expiry_notification_template_string == "NA":
                expiry_notification_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/ExpiryNotificationTemplate.html", 'r', encoding='utf-8-sig')
                expiry_notification_template_string = expiry_notification_template_file.read()
            if row_template_string == "NA":
                row_template = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/ExpiryNotificationRowTemplate.html", 'r', encoding='utf-8-sig')
                row_template_string = row_template.read()

            # -------------------------- Get company info from db ---------------------------

            software_logo = list(Company.objects.using(db_name).all().values_list('software_logo', flat=True))[0]

            # ------------------------------- Add header ------------------------------------

            if config.custom_text is not None:
                expiry_notification_template_string = expiry_notification_template_string.replace(custom_text, config.custom_text)

            # ---------------- Replace placeholders in expiry notification template ----------------

            expiry_notification_template_string = expiry_notification_template_string.replace(start_date, str(start))
            expiry_notification_template_string = expiry_notification_template_string.replace(end_date, str(end))
            expiry_notification_template_string = expiry_notification_template_string.replace(logo, software_logo)

            for key, value in expiry_dict.items():
                cur_vin = str(key)
                cur_expiring_items = ", ".join(value)
                cur_row_template_string = row_template_string.replace(vin, cur_vin)
                cur_row_template_string = cur_row_template_string.replace(expiring_items, cur_expiring_items)
                expiry_notification_template_string = expiry_notification_template_string.replace(row_insert_string, cur_row_template_string)

            # ----------------------- Show/Hide fields based on config ------------------------

            if config.custom_text is None:
                start = "<!-- CUSTOM_TEXT START -->"
                end = "<!-- CUSTOM_TEXT END -->"
                expiry_notification_template_string = HelperMethods.replace_substring(expiry_notification_template_string, start, end, PdfManager.td_none)

            config_fields = None
            if config.fields is not None:
                config_fields = NotificationHelper.parse_fields_to_list(config.fields)

            if config_fields is not None:
                
                mutable_fields = [
                    "vin", "expiring_items"
                ]

                for field in mutable_fields:
                    if field not in config_fields:
                        start, end = '<!-- ' + str(field ) + ' START -->', '<!-- ' + str(field) + ' END -->'
                        expiry_notification_template_string = HelperMethods.replace_substring(expiry_notification_template_string, start, end, "")

            return expiry_notification_template_string

        except Exception as e:
            Logger.getLogger().error(e)
            return "Failed to generate expiry notification email. Please contact administrator."


    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_daily_op_check_notification_email(daily_op_check, request_data, check_fields, config, user):
        vin = "%VIN%"
        created_by = "%created_by%"
        date = "%date_created%"
        mileage = "%mileage%"
        hours = "%hours%"
        daily_check_name = "%daily_check_name%"
        daily_check_status = "%daily_check_status%"

        custom_text = "%CUSTOM_TEXT%"

        logo = "%logo%"
        
        try:
            # ---------- Get templates required to build daily operational check string --------------
                
            daily_op_check_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/DailyCheckNotificationTemplate.html", 'r', encoding='utf-8-sig')
            daily_check_row_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/DailyCheckNotificationRow.html", "r", encoding="utf-8-sig")
            daily_op_check_template_string = daily_op_check_template_file.read()
            daily_check_row_template_string = daily_check_row_template_file.read()

            # -------------------------- Get company info from db ---------------------------

            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            # ------------------------------- Add header ------------------------------------

            if config.custom_text is not None:
                daily_op_check_template_string = daily_op_check_template_string.replace(custom_text, config.custom_text)

            # --------------- Replace placeholders in daily check notification template ---------------

            daily_op_check_template_string = daily_op_check_template_string.replace(vin, str(daily_op_check.VIN))
            daily_op_check_template_string = daily_op_check_template_string.replace(created_by, str(daily_op_check.created_by))
            daily_op_check_template_string = daily_op_check_template_string.replace(date, str(daily_op_check.date_created))
            daily_op_check_template_string = daily_op_check_template_string.replace(logo, str(detailed_user.company.software_logo))

            if daily_op_check.mileage == -1 or daily_op_check.mileage == None:
                daily_op_check_template_string = daily_op_check_template_string.replace(mileage, "NA")
            else:
                daily_op_check_template_string = daily_op_check_template_string.replace(mileage, str(daily_op_check.mileage))
            
            if daily_op_check.hours == -1 or daily_op_check.hours == None:
                daily_op_check_template_string = daily_op_check_template_string.replace(hours, "NA")
            else:
                daily_op_check_template_string = daily_op_check_template_string.replace(hours, str(daily_op_check.hours))

            for field in check_fields:
                title_case_field = field[0].upper() + field[1:]
                customCheckRow = daily_check_row_template_string.replace(daily_check_name, title_case_field)
                if not HelperMethods.validate_bool(request_data.get(field)):
                    customCheckRow = customCheckRow.replace(daily_check_status, "Unsatisfactory")
                else:
                    customCheckRow = customCheckRow.replace(daily_check_status, "Satisfactory")
                daily_op_check_template_string = daily_op_check_template_string.replace("<!-- Insert Check Here -->", customCheckRow)

            # ----------------------- Show/Hide fields based on config ------------------------

            if config.custom_text is None:
                start = "<!-- CUSTOM_TEXT START -->"
                end = "<!-- CUSTOM_TEXT END -->"
                daily_op_check_template_string = HelperMethods.replace_substring(daily_op_check_template_string, start, end, PdfManager.td_none)

            config_fields = None
            if config.fields is not None:
                config_fields = NotificationHelper.parse_fields_to_list(config.fields)

            if config_fields is not None:
                
                mutable_fields = [
                    "vin", "created_by", "date", "mileage", "hours", "daily_check_name", "daily_check_status"
                ]

                for field in mutable_fields:
                    if field not in config_fields:
                        start, end = '<!-- ' + str(field ) + ' START -->', '<!-- ' + str(field) + ' END -->'
                        daily_op_check_template_string = HelperMethods.replace_substring(daily_op_check_template_string, start, end, "")

            return daily_op_check_template_string

        # Return nothing because generation of the html string has failed
        except Exception as e:
            Logger.getLogger().error(e)
            return "Failed to generate daily op check notification email. Please contact administrator."

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_updated_daily_ops_check_report(daily_checks, updated_daily_checks, old_values, config, user):

         # ---------------------------- placeholders ------------------------------
        daily_op_checks_id = "%id%"
        daily_op_checks_manufacturer = "%manufacturer%"
        daily_op_checks_asset_type = "%asset_type%"
        daily_op_checks_model = "%model%"
        vin = "%vin%"
        modified_by = "%modified_by%"
        prev_mileage = "%old_mileage%"
        updated_mileage = "%new_mileage%"
        prev_hours = "%old_hours%"
        updated_hours = "%new_hours%"
        prev_fuel = "%old_fuel%"
        updated_fuel = "%new_fuel%"

        custom_text = "%CUSTOM_TEXT%"

        logo = "%logo%"

        try:
            
            # ---------- Get templates required to build asset request html string -----------

            daily_ops_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/UpdatedDailyOpsTemplate.html", 'r', encoding='utf-8-sig')
            daily_ops_template_string = daily_ops_template_file.read()

            # -------------------------- Get company info from db ---------------------------

            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            
            # ------------------------------- Add header ------------------------------------

            if config.custom_text is not None:
                daily_ops_template_string = daily_ops_template_string.replace(custom_text, config.custom_text)

            # ---------------- Replace placeholders in asset request template ----------------

            if old_values.get('mileage') is None:
                miles_list = [daily_checks.mileage, updated_daily_checks.mileage]
                old_values['mileage'] = miles_list
            if old_values.get('hours') is None:
                hours_list = [daily_checks.hours, updated_daily_checks.hours] 
                old_values['hours'] = hours_list
            if old_values.get('fuel') is None:
                fuel_list = [daily_checks.fuel, updated_daily_checks.fuel] 
                old_values['fuel'] = fuel_list

            daily_ops_template_string = daily_ops_template_string.replace(daily_op_checks_id, str(updated_daily_checks.daily_check_id))
            daily_ops_template_string = daily_ops_template_string.replace(daily_op_checks_manufacturer, str(HelperMethods.check_none_type_obj(updated_daily_checks,"VIN","equipment_type","manufacturer")))
            daily_ops_template_string = daily_ops_template_string.replace(daily_op_checks_asset_type, str(HelperMethods.check_none_type_obj(updated_daily_checks,"VIN","equipment_type","asset_type")))
            daily_ops_template_string = daily_ops_template_string.replace(daily_op_checks_model, str(HelperMethods.check_none_type_obj(updated_daily_checks,"VIN","equipment_type","model_number")))
            daily_ops_template_string = daily_ops_template_string.replace(vin, str(updated_daily_checks.VIN))
            daily_ops_template_string = daily_ops_template_string.replace(modified_by, str(updated_daily_checks.modified_by))
            daily_ops_template_string = daily_ops_template_string.replace(prev_mileage, str(old_values['mileage']))
            daily_ops_template_string = daily_ops_template_string.replace(updated_mileage, str(updated_daily_checks.mileage))
            daily_ops_template_string = daily_ops_template_string.replace(prev_hours, str(old_values['hours']))
            daily_ops_template_string = daily_ops_template_string.replace(updated_hours, str(updated_daily_checks.hours))
            daily_ops_template_string = daily_ops_template_string.replace(prev_fuel, str(old_values['fuel']))
            daily_ops_template_string = daily_ops_template_string.replace(updated_fuel, str(updated_daily_checks.fuel))

            daily_ops_template_string = daily_ops_template_string.replace(logo, str(detailed_user.company.software_logo))

            # ----------------------- Show/Hide fields based on config ------------------------

            if config.custom_text is None:
                start = "<!-- CUSTOM_TEXT START -->"
                end = "<!-- CUSTOM_TEXT END -->"
                daily_ops_template_string = HelperMethods.replace_substring(daily_ops_template_string, start, end, PdfManager.td_none)

            config_fields = None
            if config.fields is not None:
                config_fields = NotificationHelper.parse_fields_to_list(config.fields)

            if config_fields is not None:
                
                mutable_fields = [
                        "daily_op_checks_id", "daily_op_checks_manufacturer", "daily_op_checks_asset_type", "daily_op_checks_model",
                        "vin", "modified_by", "prev_mileage", "updated_mileage", "prev_hours", "updated_hours", "prev_fuel", "updated_fuel"
                    ]

                for field in mutable_fields:
                    if field not in config_fields:
                        start, end = '<!-- ' + str(field ) + ' START -->', '<!-- ' + str(field) + ' END -->'
                        daily_ops_template_string = HelperMethods.replace_substring(daily_ops_template_string, start, end, "")

            # Return html string and pdf attachment location
            return daily_ops_template_string

        # Return nothing because generation of the html string has failed
        except Exception as e:
            Logger.getLogger().error(e)
            return None, "Failed to generate updated asset transfer report. Please contact administrator."

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_request_cancellation_email(service_name, service_id, config, user, location_name):

        service = "%SERVICE%"
        id = "%ID%"
        email = "%EMAIL%"
        company_name = "%COMPANY%"
        location = "%LOCATION%"

        custom_text = "%CUSTOM_TEXT%"

        logo = "%logo%"

        try:
            # ---------- Get templates required to build request cancellation html string -----------
            req_cancellation_template_file = codecs.open(HelperMethods.GetCurModuleDir() + "/FileManager/Files/RequestCancellation.html", 'r', encoding='utf-8-sig')
            req_cancellation_template_string = req_cancellation_template_file.read()

            # -------------------------- Get company info from db ---------------------------

            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)

            # ------------------------------- Add header ------------------------------------

            if config.custom_text is not None:
                req_cancellation_template_string = req_cancellation_template_string.replace(custom_text, config.custom_text)

            # ---------------- Replace placeholders in request cancellation template ----------------
            req_cancellation_template_string = req_cancellation_template_string.replace(service, service_name)
            req_cancellation_template_string = req_cancellation_template_string.replace(id, service_id)
            req_cancellation_template_string = req_cancellation_template_string.replace(email, user.email)
            req_cancellation_template_string = req_cancellation_template_string.replace(company_name, str(detailed_user.company.company_name))
            req_cancellation_template_string = req_cancellation_template_string.replace(location, location_name)

            req_cancellation_template_string = req_cancellation_template_string.replace(logo, str(detailed_user.company.software_logo))

            # ----------------------- Show/Hide fields based on config ------------------------

            if config.custom_text is None:
                start = "<!-- CUSTOM_TEXT START -->"
                end = "<!-- CUSTOM_TEXT END -->"
                req_cancellation_template_string = HelperMethods.replace_substring(req_cancellation_template_string, start, end, PdfManager.td_none)

            config_fields = None
            if config.fields is not None:
                config_fields = NotificationHelper.parse_fields_to_list(config.fields)

            if config_fields is not None:
                
                mutable_fields = [
                    ]

                for field in mutable_fields:
                    if field not in config_fields:
                        start, end = '<!-- ' + str(field ) + ' START -->', '<!-- ' + str(field) + ' END -->'
                        daily_ops_template_string = HelperMethods.replace_substring(daily_ops_template_string, start, end, "")

            return req_cancellation_template_string, f"{location_name} {service_name} ID:{service_id} Cancelled - Auto-Generated Email"
        except Exception as e:
            Logger.getLogger().error(e)
            return f"Failed to generate {service_name} request cancellation email. Please contact administrator."

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def gen_suspicious_fuel_html(user,asset,fuel_cost,header,message):
        try:
            file=codecs.open(HelperMethods.GetCurModuleDir()+"/FileManager/Files/SuspiciousFuelTemplate.html","r",encoding="utf-8-sig")
            string=file.read()
            
            detailed_user=UserHelper.get_detailed_user_obj(user.email,user.db_access)
            string=string.replace("%logo%",str(detailed_user.company.software_logo))

            string=string.replace("%header%",header)
            messageWithBolds=message
            boldCount=0
            while "\"" in messageWithBolds:
                thing="<b>"
                if boldCount%2==1:
                    thing="</b>"
                messageWithBolds=messageWithBolds.replace("\"",thing,1)
                boldCount+=1
            string=string.replace("%message%",messageWithBolds)
            string=string.replace("%vin%",asset.VIN)
            string=string.replace("%unit.number%",asset.unit_number or "N/A")
            location="N/A"
            if asset.current_location:
                location=asset.current_location.location_name
            string=string.replace("%location%",location)
            string=string.replace("%fuel.type%",fuel_cost.fuel_type.name)
            string=string.replace("%volume%","%d %s(s)"%(fuel_cost.volume,fuel_cost.volume_unit))
            string=string.replace("%cost%","%d %s(s)"%(fuel_cost.total_cost,fuel_cost.currency.name))
            string=string.replace("%name%","%s %s"%(user.first_name,user.last_name))
            string=string.replace("%email%",user.email)
            
            return string
        except:
            traceback.print_exc()
            return None

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # NOTE: Can not handle any javascript.
    '''@staticmethod
    def HtmlToPdf(source_html, output_filename):
        # open output file for writing (truncated binary)
        result_file = open(output_filename, "w+b")

        # convert HTML to PDF
        pisa_status = pisa.CreatePDF(
                source_html,                # the HTML to convert
                dest=result_file)           # file handle to recieve result

        # close output file
        result_file.close()                 # close output file

        # return False on success and True on errors
        return pisa_status.err'''

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gen_pdf_from_html_with_pdfkit(file_path, html_string):
        file_type = 'application/pdf'
        file_info = FileInfo(file_type=file_type, file_path=file_path, file_name=file_path.split('\\')[-1])
        # pdf_kit_config = {
        #     "disable-local-file-access":""
        # }
        pdfkit.from_string(html_string, str(file_path))
        #PdfManager.HtmlToPdf(html_string, str(file_path))
        return file_info

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    template_dict = {
        'maintenance_forecast_notification_template': '/FileManager/Files/MaintenanceForecastNotificationTemplate.html',
        'maintenance_forecast_notification_row_template': '/FileManager/Files/MaintenanceForecastNotificationRowTemplate.html',
        'maintenance_forecast_overdue_notification_template': '/FileManager/Files/MaintenanceForecastOverdueTemplate.html',
        'maintenance_forecast_overdue_notification_row_template': '/FileManager/Files/MaintenanceForecastOverdueRowTemplate.html',
        'expiry_notification_template': '/FileManager/Files/ExpiryNotificationTemplate.html',
        'expiry_notification_row_template': '/FileManager/Files/ExpiryNotificationRowTemplate.html'
    }

    @staticmethod
    def read_template_file(path):
        file = codecs.open(HelperMethods.GetCurModuleDir() + path, 'r', encoding='utf-8-sig')
        return file.read()
    
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------