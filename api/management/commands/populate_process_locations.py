from django.core.management.base import BaseCommand
from api.Models.repairs import RepairsModel
from api.Models.maintenance_request import MaintenanceRequestModel
from api.Models.accident_report import AccidentModel
from api.Models.asset_issue import AssetIssueModel
from api.Models.approval import Approval
from api.Models.asset_daily_checks import AssetDailyChecksModel
from api.Models.asset_disposal import AssetDisposalModel
from api.Models.asset_log import AssetLog
from api.Models.asset_request import AssetRequestModel
from api.Models.asset_transfer import AssetTransfer
from api.Models.Cost.insurance_cost import InsuranceCost
from api.Models.Cost.labor_cost import LaborCost
from api.Models.Cost.license_cost import LicenseCost
from api.Models.Cost.parts import Parts
from api.Models.Cost.rental_cost import RentalCost
from api.Models.locations import LocationModel
from api.Models.maintenance_forecast import MaintenanceForecastRules


class Command(BaseCommand):
    help = "Populate business unit table from Department field in asset model"

    def handle(self, *args, **kwargs):
        
        databases = ["dev", "westjet", "gbcs", "district_of_houston", "traxx", "schlumberger", "fmt", "mobile_app"]

        for db_name in databases:
            print("-----------------------------------------")
            print("Updating database: " + str(db_name))
            print("-----------------------------------------")
            Command.update_maintenance_forecast_rule_location(db_name)
            # Command.update_repair_location(db_name)
            # Command.update_maintenance_location(db_name)
            # Command.update_accident_location(db_name)
            # Command.update_issue_location(db_name)
            # Command.update_approval_location(db_name)
            # Command.update_daily_check_location(db_name)
            # Command.update_disposal_location(db_name)
            # Command.update_asset_log_location(db_name)
            # Command.update_asset_request_location(db_name)
            # Command.update_asset_transfer_location(db_name)
            # Command.update_license_cost_location(db_name)
            # Command.update_labor_cost_location(db_name)
            # Command.update_parts_cost_location(db_name)
            # Command.update_insurance_cost_location(db_name)
            # Command.update_rental_cost_location(db_name)

    @staticmethod
    def update_maintenance_forecast_rule_location(db_name):
        maintenance_rules = MaintenanceForecastRules.objects.using(db_name).all()

        for maintenance_rule in maintenance_rules:
            try:
                print("Setting maintenance rule " + str(maintenance_rule.custom_id) + " location to " + str(maintenance_rule.VIN.current_location))
                maintenance_rule.location = maintenance_rule.VIN.current_location
                maintenance_rule.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_repair_location(db_name):
        repairs = RepairsModel.objects.using(db_name).all()

        for repair in repairs:
            try:
                print("Setting repair " + str(repair.repair_id) + " location to " + str(repair.VIN.current_location))
                repair.location = repair.VIN.current_location
                repair.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_maintenance_location(db_name):
        maintenances = MaintenanceRequestModel.objects.using(db_name).all()

        for maintenance in maintenances:
            try:
                print("Setting maintenance " + str(maintenance.maintenance_id) + " location to " + str(maintenance.VIN.current_location))
                maintenance.location = maintenance.VIN.current_location
                maintenance.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_accident_location(db_name):
        accidents = AccidentModel.objects.using(db_name).all()

        for accident in accidents:
            try:
                print("Setting accident " + str(accident.accident_id) + " location to " + str(accident.VIN.current_location))
                accident.location = accident.VIN.current_location
                accident.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_issue_location(db_name):
        issues = AssetIssueModel.objects.using(db_name).all()

        for issue in issues:
            try:
                print("Setting issue " + str(issue.issue_id) + " location to " + str(issue.VIN.current_location))
                issue.location = issue.VIN.current_location
                issue.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_approval_location(db_name):
        approvals = Approval.objects.using(db_name).all()

        for approval in approvals:
            try:
                print("Setting approval " + str(approval.approval_id) + " location to " + str(approval.asset_transfer_request.VIN.current_location))
                approval.location = approval.asset_transfer_request.VIN.current_location
                approval.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue
            
    @staticmethod
    def update_daily_check_location(db_name):
        daily_checks = AssetDailyChecksModel.objects.using(db_name).all()

        for check in daily_checks:
            try:
                print("Setting check " + str(check.daily_check_id) + " location to " + str(check.VIN.current_location))
                check.location = check.VIN.current_location
                check.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_disposal_location(db_name):
        disposals = AssetDisposalModel.objects.using(db_name).all()

        for disposal in disposals:
            try:
                print("Setting disposal " + str(disposal.id) + " location to " + str(disposal.VIN.current_location))
                disposal.location = disposal.VIN.current_location
                disposal.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_asset_log_location(db_name):
        asset_log = AssetLog.objects.using(db_name).all()

        for log in asset_log:
            try:
                print("Setting log " + str(log.asset_log_id) + " location to " + str(log.VIN.current_location))
                log.location = log.VIN.current_location
                log.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_asset_request_location(db_name):
        asset_requests = AssetRequestModel.objects.using(db_name).all()

        for asset_request in asset_requests:
            try:
                print("Asset request " + str(asset_request.id) + " location to " + str(asset_request.business_unit.location))
                asset_request.location = asset_request.business_unit.location
                asset_request.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_asset_transfer_location(db_name):
        asset_transfers = AssetTransfer.objects.using(db_name).all()

        for asset_transfer in asset_transfers:
            try:
                print("Asset transfer " + str(asset_transfer.asset_transfer_id) + " location to " + str(asset_transfer.VIN.original_location))
                asset_transfer.original_location = asset_transfer.VIN.original_location
                asset_transfer.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def find_location_from_process_fk(obj, default_loc):
        try:
            if obj.maintenance is not None:
                return obj.maintenance.VIN.current_location
        except Exception:
            pass
        try:
            if obj.issue is not None:
                return obj.issue.VIN.current_location
        except Exception:
            pass
        try:
            if obj.repair is not None:
                return obj.repair.VIN.current_location
        except Exception:
            pass
        try:
            if obj.accident is not None:
                return obj.accident.VIN.current_location
        except Exception:
            pass
        try:
            if obj.asset_request is not None:
                return obj.asset_request.business_unit.current_location
        except Exception:
            pass
        try:
            if obj.disposal is not None:
                return obj.disposal.VIN.current_location
        except Exception:
            pass
        try:
            if obj.transfer is not None:
                return obj.transfer.VIN.current_location
        except Exception:
            pass
        print("Could not find location... assigning location_id 1.")
        return 1

    @staticmethod
    def update_insurance_cost_location(db_name):
        insurance_cost = InsuranceCost.objects.using(db_name).all()
        default_location = LocationModel.objects.using(db_name).get(location_id=1)
        for cost in insurance_cost:
            try:
                location = Command.find_location_from_process_fk(cost, default_location)
                print("Asset insurance cost " + str(cost.id) + " location to " + str(location))
                cost.location = location
                cost.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_labor_cost_location(db_name):
        labor_cost = LaborCost.objects.using(db_name).all()
        default_location = LocationModel.objects.using(db_name).get(location_id=1)
        for cost in labor_cost:
            try:
                location = Command.find_location_from_process_fk(cost, default_location)
                print("Asset labor cost " + str(cost.id) + " location to " + str(location))
                cost.location = location
                cost.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_license_cost_location(db_name):
        license_cost = LicenseCost.objects.using(db_name).all()

        for cost in license_cost:
            try:
                print("Asset license cost " + str(cost.id) + " location to " + str(cost.VIN.current_location))
                cost.location = cost.VIN.current_location
                cost.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_parts_cost_location(db_name):
        parts_cost = Parts.objects.using(db_name).all()
        default_location = LocationModel.objects.using(db_name).get(location_id=1)
        for cost in parts_cost:
            try:
                location = Command.find_location_from_process_fk(cost, default_location)
                print("Asset parts cost " + str(cost.id) + " location to " + str(location))
                cost.location = location
                cost.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue

    @staticmethod
    def update_rental_cost_location(db_name):
        rental_cost = RentalCost.objects.using(db_name).all()
        default_location = LocationModel.objects.using(db_name).get(location_id=1)
        for cost in rental_cost:
            try:
                location = Command.find_location_from_process_fk(cost, default_location)
                print("Asset rental cost " + str(cost.id) + " location to " + str(location))
                cost.location = location
                cost.save()
            except Exception as e:
                print(e)
                print("Skipping to next entry...")
                continue
    
