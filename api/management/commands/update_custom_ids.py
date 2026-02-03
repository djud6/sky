from django.core.management.base import BaseCommand
from api.Models.repairs import RepairsModel
from api.Models.maintenance_request import MaintenanceRequestModel
from api.Models.maintenance_forecast import MaintenanceForecastRules
from api.Models.accident_report import AccidentModel
from api.Models.asset_issue import AssetIssueModel
from api.Models.asset_daily_checks import AssetDailyChecksModel
from api.Models.asset_disposal import AssetDisposalModel
from api.Models.asset_request import AssetRequestModel

from api.Models.asset_transfer import AssetTransfer
from core.CompanyManager.CompanyHelper import CompanyHelper


class Command(BaseCommand):
    help = "Update custom_id/work_order for all models."

    def handle(self, *args, **kwargs):

        # databases = ["dev", "westjet", "gbcs", "district_of_houston", "traxx", "schlumberger", "fmt"]
        databases = ["dev_demo_aukai"]

        for db_name in databases:
            print("-----------------------------------------")
            print("Updating database: " + str(db_name))
            print("-----------------------------------------")
            company_name = str(CompanyHelper.get_list_companies(db_name)[0].company_name)
            Command.update_repair_work_order(company_name, db_name)
            Command.update_maintenance_work_order(company_name, db_name)
            Command.update_maintenance_rule_custom_id(company_name, db_name)
            Command.update_accident_custom_id(company_name, db_name)
            Command.update_issue_custom_id(company_name, db_name)
            Command.update_daily_check_custom_id(company_name, db_name)
            Command.update_disposal_custom_id(company_name, db_name)
            Command.update_asset_transfer_custom_id(company_name, db_name)
            Command.update_asset_request_custom_id(company_name, db_name)

    @staticmethod
    def update_repair_work_order(company_name, db_name):
        repairs = RepairsModel.objects.using(db_name).all()

        for repair in repairs:
            try:
                print("Setting repair " + str(repair.repair_id) + " work_order to " + company_name + "-r-" + str(repair.repair_id))
                repair.work_order = company_name + "-r-" + str(repair.repair_id)
                repair.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_maintenance_work_order(company_name, db_name):
        maintenances = MaintenanceRequestModel.objects.using(db_name).all()

        for maintenance in maintenances:
            try:
                print("Setting maintenance " + str(maintenance.maintenance_id) + " work_order to " + company_name + "-m-" + str(maintenance.maintenance_id))
                maintenance.work_order = company_name + "-m-" + str(maintenance.maintenance_id)
                maintenance.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_maintenance_rule_custom_id(company_name, db_name):
        maintenance_rules = MaintenanceForecastRules.objects.using(db_name).all()

        for rule in maintenance_rules:
            try:
                print("Setting maintenance rule " + str(rule.id) + " custom_id to " + company_name + "-mfr-" + str(rule.id))
                rule.custom_id = company_name + "-mfr-" + str(rule.id)
                rule.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_accident_custom_id(company_name, db_name):
        accidents = AccidentModel.objects.using(db_name).all()

        for accident in accidents:
            try:
                print("Setting accident " + str(accident.accident_id) + " custom_id to " + company_name + "-a-" + str(accident.accident_id))
                accident.custom_id = company_name + "-a-" + str(accident.accident_id)
                accident.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_issue_custom_id(company_name, db_name):
        issues = AssetIssueModel.objects.using(db_name).all()

        for issue in issues:
            try:
                print("Setting issue " + str(issue.issue_id) + " custom_id to " + company_name + "-i-" + str(issue.issue_id))
                issue.custom_id = company_name + "-i-" + str(issue.issue_id)
                issue.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_daily_check_custom_id(company_name, db_name):
        daily_checks = AssetDailyChecksModel.objects.using(db_name).all()

        for check in daily_checks:
            try:
                print("Setting check " + str(check.daily_check_id) + " custom_id to " + company_name + "-dc-" + str(check.daily_check_id))
                check.custom_id = company_name + "-dc-" + str(check.daily_check_id)
                check.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_disposal_custom_id(company_name, db_name):
        disposals = AssetDisposalModel.objects.using(db_name).all()

        for disposal in disposals:
            try:
                print("Setting disposal " + str(disposal.id) + " custom_id to " + company_name + "-d-" + str(disposal.id))
                disposal.custom_id = company_name + "-d-" + str(disposal.id)
                disposal.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_asset_transfer_custom_id(company_name, db_name):
        asset_transfers = AssetTransfer.objects.using(db_name).all()

        for asset_transfer in asset_transfers:
            try:
                print("Asset transfer " + str(asset_transfer.asset_transfer_id) + " custom_id to " + company_name + "-t-" + str(asset_transfer.asset_transfer_id))
                asset_transfer.custom_id = company_name + "-t-" + str(asset_transfer.asset_transfer_id)
                asset_transfer.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_asset_request_custom_id(company_name, db_name):
        asset_requests = AssetRequestModel.objects.using(db_name).all()

        for asset_request in asset_requests:
            try:
                print("Asset request " + str(asset_request.id) + " custom_id to " + company_name + "-ar-" + str(asset_request.id))
                asset_request.custom_id = company_name + "-ar-" + str(asset_request.id)
                asset_request.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue
