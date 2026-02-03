from core.AssetManager.AssetHelper import AssetHelper
from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_model_history import AssetModelHistory
from api.Models.asset_model import AssetModel
from api.Serializers.serializers import AssetModelHistorySerializer
from api.Models.asset_log import AssetLog
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class AssetHistory:

    @staticmethod
    def create_asset_record(VIN, db_name):
        try:
            asset = AssetModel.objects.using(db_name).get(VIN=VIN)
            asset_history_entry = AssetHistory.generate_asset_history_entry(asset)
            asset_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def create_bulk_asset_records_by_VINs(VINs, db_name):
        try:
            assets = list(AssetHelper.get_assets_from_VIN_list(VINs, db_name).values())
            formatted_assets_list = []
            for asset in assets:
                asset['parent'] = asset['parent_id']
                asset['equipment_type'] = asset['equipment_type_id']
                asset['company'] = asset['company_id']
                asset['original_location'] = asset['original_location_id']
                asset['current_location'] = asset['current_location_id']
                asset['department'] = asset['department_id']
                asset['job_specification'] = asset['job_specification_id']
                asset['currency'] = asset['currency_id']
                asset['modified_by'] = asset['modified_by_id']
                formatted_assets_list.append(asset)

            ser = AssetModelHistorySerializer(data=formatted_assets_list, many=True)
            if(ser.is_valid()):
                ser.save()
                return True
            return False
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def create_asset_record_by_obj(asset):
        try:
            asset_history_entry = AssetHistory.generate_asset_history_entry(asset)
            asset_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_asset_history_entry(asset):
        return AssetModelHistory(
            VIN=asset,
            parent=asset.parent,
            equipment_type=asset.equipment_type,
            company=asset.company,
            jde_department=asset.jde_department,
            original_location=asset.original_location,
            current_location=asset.current_location,
            status=asset.status,
            unit_number=asset.unit_number,
            license_plate=asset.license_plate,
            department=asset.department,
            job_specification=asset.job_specification,
            fire_extinguisher_quantity=asset.fire_extinguisher_quantity,
            fire_extinguisher_inspection_date=asset.fire_extinguisher_inspection_date,
            path=asset.path,
            last_process=asset.last_process,
            hours_or_mileage=asset.hours_or_mileage,
            mileage=asset.mileage,
            hours=asset.hours,
            mileage_unit=asset.mileage_unit,
            total_cost=asset.total_cost,
            currency=asset.currency,
            daily_average_hours=asset.daily_average_hours,
            daily_average_mileage=asset.daily_average_mileage,
            replacement_hours=asset.replacement_hours,
            replacement_mileage=asset.replacement_mileage,
            load_capacity=asset.load_capacity,
            load_capacity_unit=asset.load_capacity_unit,
            fuel=asset.fuel,
            engine=asset.engine,
            modified_by=asset.modified_by,
            fuel_tank_capacity=asset.fuel_tank_capacity,
            fuel_tank_capacity_unit=asset.fuel_tank_capacity_unit,
            is_rental=asset.is_rental,
            monthly_subscription_cost=asset.monthly_subscription_cost,
            class_code = asset.class_code,
            asset_description=asset.asset_description,
            custom_fields=asset.custom_fields
        )

    @staticmethod
    def generate_asset_log_event_entry(asset_obj, event_type, event_id, user, description, location):
        return AssetLog(
            VIN=asset_obj,
            log_type=AssetLog.event,
            event_type=event_type,
            event_id=event_id,
            created_by=user,
            modified_by=user,
            content= "Event: " + description,
            location=location
        )
