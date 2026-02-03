from django.core.management.base import BaseCommand
from api.Models.asset_log import AssetLog
from core.CompanyManager.CompanyHelper import CompanyHelper


class Command(BaseCommand):
    help = "Update custom_id/work_order for all models."

    def handle(self, *args, **kwargs):

        databases = ["dev_demo_aukai"]

        for db_name in databases:
            print("-----------------------------------------")
            print("Updating database: " + str(db_name))
            print("-----------------------------------------")
            company_name = str(CompanyHelper.get_list_companies(db_name)[0].company_name)
            Command.update_asset_log_ids(company_name, db_name)

    @staticmethod
    def update_asset_log_ids(company_name, db_name):
        asset_log = AssetLog.objects.using(db_name).all()

        for log in asset_log:
            try:
                original_event_id = int(log.event_id)
                identifier = Command.get_identifier(log.event_type)
                print("Setting asset log event " + str(log.asset_log_id) + " ID to " + company_name + identifier + str(log.asset_log_id))
                log.event_id = company_name + identifier + str(original_event_id)
                log.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def get_identifier(event_type):
        if event_type == AssetLog.accident:
            return "-a-"
        if event_type == AssetLog.issue:
            return "-i-"
        if event_type == AssetLog.repair:
            return "-r-"
        if event_type == AssetLog.maintenance:
            return "-m-"
        if event_type == AssetLog.maintenance_rule:
            return "-mfr-"
        if event_type == AssetLog.disposal:
            return "-d-"
        if event_type == AssetLog.transfer:
            return "-t-"
        if event_type == AssetLog.operator_check:
            return "-dc-"
