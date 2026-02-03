from datetime import datetime
from django.db.models.fields import SlugField
from core.Helper import HelperMethods
from rest_framework.fields import ReadOnlyField
from api.Models.Cost.delivery_cost import DeliveryCost
from api.Models.maintenance_request_file import MaintenanceRequestFile
from decimal import Context
from api.Models.transfer_file import TransferFile
from rest_framework import serializers

from ..Models.approved_vendor_departments import ApprovedVendorDepartments
from ..Models.approved_vendor_tasks import ApprovedVendorTasks
from ..Models.asset_model import AssetModel
from ..Models.Snapshot.snapshot_daily_asset import SnapshotDailyAsset
from ..Models.asset_file import AssetFile
from ..Models.asset_model_history import AssetModelHistory
from ..Models.job_specification import JobSpecification
from ..Models.asset_issue import AssetIssueModel
from ..Models.asset_issue_category import AssetIssueCategory
from ..Models.asset_issue_history import AssetIssueModelHistory
from ..Models.asset_issue_file import AssetIssueFileModel
from ..Models.asset_daily_checks import AssetDailyChecksModel
from ..Models.asset_daily_checks_history import AssetDailyChecksModelHistory
from ..Models.asset_daily_checks_comment import AssetDailyChecksComment
from ..Models.asset_type import AssetTypeModel
from ..Models.asset_type_checks import AssetTypeChecks
from ..Models.asset_type_checks_history import AssetTypeChecksHistory
from ..Models.asset_manufacturer import AssetManufacturerModel
from ..Models.fuel_type import FuelType
from ..Models.equipment_type import EquipmentTypeModel
from ..Models.business_unit import BusinessUnitModel
from ..Models.cost_centre import CostCentreModel
from ..Models.asset_request_justification import AssetRequestJustificationModel
from ..Models.asset_request import AssetRequestModel
from core.ParsingManager.ParsingHelper import ParsingHelper
from core.VendorManager.VendorHelper import VendorHelper
from ..Models.asset_request_file import AssetRequestFile
from ..Models.asset_request_history import AssetRequestModelHistory
from ..Models.approved_vendors import ApprovedVendorsModel
from ..Models.asset_disposal import AssetDisposalModel
from ..Models.asset_disposal_history import AssetDisposalModelHistory
from ..Models.asset_disposal_file import AssetDisposalFile
from ..Models.accident_report import AccidentModel
from ..Models.accident_report_history import AccidentModelHistory
from ..Models.accident_file import AccidentFileModel
from ..Models.repairs import RepairsModel
from ..Models.repairs_history import RepairsModelHistory
from ..Models.repair_file import RepairFile
from ..Models.inspection_type import InspectionTypeModel
from ..Models.maintenance_request import MaintenanceRequestModel
from ..Models.maintenance_request_history import MaintenanceRequestModelHistory
from ..Models.locations import LocationModel
from ..Models.maintenance_forecast import MaintenanceForecastRules
from ..Models.maintenance_forecast_history import MaintenanceForecastRulesHistory
from ..Models.fleet_guru import FleetGuru
from ..Models.RolePermissions import RolePermissions
from ..Models.Company import Company
from ..Models.dailyinspectionmodel import DailyInspection
from ..Models.dailyinspectionmodelhistory import DailyInspectionHistory
from ..Models.DetailedUser import DetailedUser
from ..Models.DetailedUserModelHistory import DetailedUserModelHistory
from ..Models.user_configuration import UserConfiguration
from ..Models.notification_configuration import NotificationConfiguration
from ..Models.approval import Approval
from ..Models.approval_model_history import ApprovalModelHistory
from ..Models.asset_transfer import AssetTransfer
from ..Models.asset_transfer_history import AssetTransferModelHistory
from ..Models.error_report import ErrorReport
from ..Models.error_report_file import ErrorReportFile
from ..Models.asset_log import AssetLog
from ..Models.Cost.currency import Currency
from ..Models.Cost.parts import Parts
from ..Models.Cost.parts_history import PartsModelHistory
from ..Models.Cost.license_cost import LicenseCost
from ..Models.Cost.license_cost_history import LicenseCostModelHistory
from ..Models.Cost.labor_cost import LaborCost
from ..Models.Cost.labor_cost_history import LaborCostModelHistory
from ..Models.Cost.insurance_cost import InsuranceCost
from ..Models.Cost.insurance_cost_history import InsuranceCostModelHistory
from ..Models.Cost.rental_cost import RentalCost
from ..Models.Cost.rental_cost_history import RentalCostModelHistory
from ..Models.Cost.fuel_cost import FuelCost
from ..Models.Cost.fuel_cost_history import FuelCostModelHistory
from ..Models.fuel_card import FuelCard
from ..Models.Cost.acquisition_cost import AcquisitionCost
from ..Models.Cost.acquisition_cost_history import AcquisitionCostModelHistory
from ..Models.Snapshot.snapshot_daily_location_cost import SnapshotDailyLocationCost
from ..Models.Snapshot.snapshot_daily_counts import SnapshotDailyCounts
from ..Models.Cost.delivery_cost_history import DeliveryCostHistory
from ..Models.engine import EngineModel,EngineHistoryModel,EngineHistoryAction
from ..Models.user_table_layout import UserTableLayoutModel
from ..Models.request_quote import RequestQuote
from ..Models.Inventory.inventory import Inventory
from ..Models.Cost.fuel_cost_check import FuelCostCheck
from ..Models.annual_report import AnnualReport
from core.Helper import HelperMethods
from multiprocessing.pool import ThreadPool
import json

# --------------------------------------------------------------------------------------------------------

class RolePermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermissions
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class DetailedUserModelHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailedUserModelHistory
        fields = "__all__"


# --------------------------------------------------------------------------------------------------------

class EngineSerializer(serializers.ModelSerializer):
    class Meta:
        model = EngineModel
        fields = ["engine_id","name","hours"]

class EngineHistorySerializer(serializers.ModelSerializer):
  
    responsible_user_email=serializers.SlugRelatedField(read_only=True,source="responsible_user",slug_field="email")
    description=serializers.SerializerMethodField()
    
    def get_description(self,history):
        verb=EngineHistoryAction[history.action].get_verb()
        date=history.date.strftime("%y-%m-%d %H:%M:%S")
        return "%s \"%s\" at %s (current hours = %.1f)"%(verb,history.updated_name,date,history.updated_hours)
  
    class Meta:
        model = EngineHistoryModel
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class UserTableLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTableLayoutModel
        fields = ["key","value"]

# --------------------------------------------------------------------------------------------------------

# TODO: these names are extremely misleading. AssetModelSerializer is actually a SUBSET of LightAssetModelSerializer!?

class AssetModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetModel
        fields = "__all__"

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        custom_fields = rep.get('custom_fields')
        if custom_fields:
            # Replacing single quotes with double quotes to make it a valid JSON string
            custom_fields = custom_fields.replace("\"", '\\"').replace("'", '"')
            # Replacing "None" with null
            custom_fields = custom_fields.replace('None', 'null')
            # Converting the JSON string to a Python dictionary
            custom_fields_dict = json.loads(custom_fields)
            # Updating the rep dictionary with the new dictionary
            rep['custom_fields'] = custom_fields_dict
        return rep

class LightAssetModelSerializer(serializers.ModelSerializer):
    asset_type = serializers.SlugRelatedField(read_only=True, source='equipment_type.asset_type', slug_field='name')
    manufacturer = serializers.SlugRelatedField(read_only=True, source='equipment_type.manufacturer', slug_field='name')
    model_number = serializers.SlugRelatedField(read_only=True, source='equipment_type', slug_field='model_number')
    fuel_type = serializers.SlugRelatedField(read_only=True, source='fuel', slug_field='name')
    department_name = serializers.SlugRelatedField(read_only=True, source='department', slug_field='name')
    businessUnit = serializers.SlugRelatedField(read_only=True, source='department', slug_field='name')
    original_location = serializers.SlugRelatedField(read_only=True, slug_field='location_name')
    current_location = serializers.SlugRelatedField(read_only=True, slug_field='location_name')
    company = serializers.SlugRelatedField(read_only=True, slug_field='company_name')
    has_disposal = serializers.SerializerMethodField()
    has_transfer = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    disposal_trade_in = serializers.SerializerMethodField()
    cost_centre_name = serializers.SlugRelatedField(read_only=True, source='cost_centre', slug_field='name')
    engines = serializers.SerializerMethodField()
    
    # for compatibility, we override `engine` value if multiple engines present (doesn't make sense to have both)
    # but don't override hours (vessel hull hours and engine hours are distinct values)
    # TODO: confirm that this is expected behavior in FE
    
    engine = serializers.SerializerMethodField()
    expiration_date = serializers.SerializerMethodField()

    def get_expiration_date(self, asset):
        expiration_dates = self.context.get('expiration_dates')
        if expiration_dates:
            return expiration_dates.get(asset.VIN) or None
        return None

    def get_engine(self, asset):
        engines = self.get_engines(asset)
        number_of_engines = len(engines)
        if number_of_engines > 0:
            output = f"Number of Engines: {number_of_engines} ("

            for engine in engines:
                output = f"{output}{engine['name']}, "
            else:
                output = f"{output[:-2]})"

            return output
        return asset.engine

    def get_engines(self, asset):
        engines = self.context.get('engines')
        asset_engines = []

        if engines:
            for engine in engines:
                if engine.get('VIN_id') == asset.VIN:
                    asset_engines.append(engine)
            return EngineSerializer(asset_engines, many=True).data
        return []

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        custom_fields = rep.get('custom_fields')
        if custom_fields:
            # Replacing single quotes with double quotes to make it a valid JSON string
            custom_fields = custom_fields.replace("\"", '\\"').replace("'", '"')
            # Replacing "None" with null
            custom_fields = custom_fields.replace('None', 'null')
            # Converting the JSON string to a Python dictionary
            custom_fields_dict = json.loads(custom_fields)
            # Updating the rep dictionary with the new dictionary
            rep['custom_fields'] = custom_fields_dict
        return rep

    def get_has_disposal(self, asset_obj):
        all_disposals = self.context.get('disposal')
        finished_status = {AssetDisposalModel.complete, AssetDisposalModel.denied, AssetDisposalModel.cancelled}
        if all_disposals:
            for item in all_disposals:
                if item['VIN'] == asset_obj.VIN:
                    if item['status'] not in finished_status:
                        return True
                    return False
        return False

    def get_has_transfer(self, asset_obj):
        all_transfers = self.context.get('transfer')
        finished_status = {AssetTransfer.denied, AssetTransfer.delivered, AssetTransfer.cancelled}
        if all_transfers:
            for item in all_transfers:
                if item['VIN'] == asset_obj.VIN:
                    if item['status'] not in finished_status:
                        return True
                    return False
        return False

    def get_children(self, asset_obj):
        asset_parent_dict_list = self.context.get('asset_parent_dict_list')
        children = []
        elems_to_remove = []
        is_parent = False
        if asset_parent_dict_list:
            for element in asset_parent_dict_list:
                if element['parent'] == asset_obj.VIN:
                    children.append(element.get('VIN'))
                    elems_to_remove.append(element)
                    is_parent = True

        if is_parent:
            self.context['asset_parent_dict_list'] = HelperMethods.delete_list_from_list(self.context['asset_parent_dict_list'], elems_to_remove)

        return children

    def get_disposal_trade_in(self, asset_obj):
        all_disposals = self.context.get('disposal')
        if all_disposals:
            for item in all_disposals:
                if item['VIN'] == asset_obj.VIN:
                    if item['disposal_type'].lower() == AssetDisposalModel.trade_in:
                        return item['id']
                    return None
        return None

    class Meta:
        model = AssetModel
        fields = "__all__"

class AssetModelHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetModelHistory
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class AssetIssueFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetIssueFileModel
        fields = "__all__"


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetIssueModel
        fields = "__all__"


class LightIssueSerializer(serializers.ModelSerializer):
    original_location = serializers.SlugRelatedField(read_only=True, source='VIN.original_location', slug_field='location_name')
    current_location = serializers.SlugRelatedField(read_only=True, source='VIN.current_location', slug_field='location_name')
    issue_location = serializers.SlugRelatedField(read_only=True, source='location', slug_field='location_name')
    asset_type = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type.asset_type', slug_field='name')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    files = serializers.SerializerMethodField()
    accident_custom_id = serializers.SlugRelatedField(read_only=True, source='accident_id', slug_field='custom_id')
    repair_work_order = serializers.SlugRelatedField(read_only=True, source='repair_id', slug_field='work_order')
    unit_number=serializers.SerializerMethodField()
    
    def get_unit_number(self, issue_obj):
        return issue_obj.VIN.unit_number

    def get_files(self, issue_obj):
        all_files = self.context.get('all_issue_files')
        
        if all_files:
            relevant_files = []
            for f in all_files:
                if f.get('issue_id') == issue_obj.issue_id:
                    relevant_files.append(f)

            return AssetIssueFileSerializer(relevant_files, many=True).data
        return []
        
    class Meta:
        model = AssetIssueModel
        fields = "__all__"


class FullIssueSerializer(serializers.ModelSerializer):
    asset = AssetModelSerializer(read_only=True, source='VIN')
    original_location = serializers.SlugRelatedField(read_only=True, source='VIN.original_location', slug_field='location_name')
    current_location = serializers.SlugRelatedField(read_only=True, source='VIN.current_location', slug_field='location_name')
    files = AssetIssueFileSerializer(read_only=True, many=True, source='assetissuefilemodel_set')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    
    class Meta:
        model = AssetIssueModel
        fields = "__all__"


class AssetIssueHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetIssueModelHistory
        fields = "__all__"


class AssetIssueCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetIssueCategory
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class AssetDailyChecksSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetDailyChecksModel
        fields = "__all__"


class LightAssetDailyChecksSerializer(serializers.ModelSerializer):
    asset_type = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type.asset_type', slug_field='name')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    daily_check_location = serializers.SlugRelatedField(read_only=True, source='location', slug_field='location_name')
    unsatisfactory = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    def get_first_last_name(self, daily_check_obj):
        users = self.context.get('users')
        for user in users:
            if user.get("email") == daily_check_obj.created_by.email:
                return user.get("first_name"), user.get("last_name")
        return "NA", "NA"

    def to_representation(self, daily_check_obj):
        data = super().to_representation(daily_check_obj)
        first_name, last_name = self.get_first_last_name(daily_check_obj)
        data['first_name'] = first_name
        data['last_name'] = last_name
        return data

    def get_comments(self, daily_check_obj):
        all_comments = self.context.get('comments')
        if all_comments:
            relevant_comments = []
            for item in all_comments:
                if item.daily_check_id == daily_check_obj.daily_check_id:
                    relevant_comments.append(item)
            return AssetDailyChecksCommentSerializer(relevant_comments, many=True).data
        return []

    def get_unsatisfactory(self, daily_check_obj):
        # list of checks to be iterated over
        non_checks = [
            "daily_check_id",
            "custom_id",
            "VIN",
            "operable",
            "mileage",
            "hours",
            "is_tagout",
            "location",
            "created_by",
            "date_created",
            "modified_by",
            "date_modified",
            "assetdailychecksmodelhistory",
            "assetdailycheckscomment",
            "enginehistorymodel"
        ]

        for field in [f.name for f in daily_check_obj._meta.get_fields()]:
            if field not in non_checks:
                check_status = getattr(daily_check_obj, field)
                # if status is defined and is a false value (0 or False is expected)
                if check_status is not None and not check_status:
                    return True
        return False

    class Meta:
        model = AssetDailyChecksModel
        fields = "__all__"


class FullAssetDailyChecksSerializer(serializers.ModelSerializer):
    asset = AssetModelSerializer(read_only=True, source='VIN')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    class Meta:
        model = AssetDailyChecksModel
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class AssetDailyChecksCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetDailyChecksComment
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------


class AssetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetTypeModel
        fields = "__all__"

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        custom_fields = rep.get('custom_fields')
        if custom_fields:
            # Replacing single quotes with double quotes to make it a valid JSON string
            custom_fields = custom_fields.replace("\"", '\\"').replace("'", '"')
            # Replacing "None" with null
            custom_fields = custom_fields.replace('None', 'null')
            # Converting the JSON string to a Python dictionary
            custom_fields_dict = json.loads(custom_fields)
            # Updating the rep dictionary with the new dictionary
            rep['custom_fields'] = custom_fields_dict
        return rep

    

# --------------------------------------------------------------------------------------------------------

class AssetTypeChecksSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetTypeChecks
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class AssetTypeChecksHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetTypeChecksHistory
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class AssetManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetManufacturerModel
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class EquipmentTypeSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.SlugRelatedField(source='manufacturer', read_only=True, slug_field='name')
    class Meta:
        model = EquipmentTypeModel
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class LightEquipmentTypeSerializer(serializers.ModelSerializer):
    manufacturer = serializers.SlugRelatedField(read_only=True, slug_field='name')
    asset_type = serializers.SlugRelatedField(read_only=True, slug_field='name')
    fuel = serializers.SlugRelatedField(read_only=True, slug_field='name')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    class Meta:
        model = EquipmentTypeModel
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class BusinessUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessUnitModel
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class CostCentreSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostCentreModel
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class AssetRequestJustificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetRequestJustificationModel
        fields = "__all__"

class AssetRequestSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        if validated_data.get('potential_vendor_ids') is None:
            validated_data['status'] = AssetRequestModel.awaiting_approval
        return AssetRequestModel.objects.create(**validated_data)

    class Meta:
        model = AssetRequestModel
        fields = "__all__"

class LightAssetRequestSerializer(serializers.ModelSerializer):
    asset_type = serializers.SlugRelatedField(read_only=True, source='equipment.asset_type', slug_field='name')
    manufacturer = serializers.SlugRelatedField(read_only=True, source='equipment.manufacturer', slug_field='name')
    model_number = serializers.SlugRelatedField(read_only=True, source='equipment', slug_field='model_number')
    engine = serializers.SlugRelatedField(read_only=True, source='equipment', slug_field='engine')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    business_unit = serializers.SlugRelatedField(read_only=True, slug_field='name')
    cost_centre = serializers.SlugRelatedField(read_only=True, slug_field='name')
    justification = serializers.SlugRelatedField(read_only=True, slug_field='name')
    location = serializers.SlugRelatedField(read_only=True, slug_field='location_name')
    vendor_name = serializers.SlugRelatedField(read_only=True, source='vendor', slug_field='vendor_name')
    disposal_custom_id = serializers.SlugRelatedField(read_only=True, source='disposal', slug_field='custom_id')
    # Following fields don't work for now
    files = serializers.SerializerMethodField()
    # quotes = serializers.SerializerMethodField()
    # has_delivery_cost = serializers.SerializerMethodField()

    def get_files(self, asset_request_obj):
        all_files = self.context.get('asset_request_files')
        if all_files:
            relevant_files = []
            for f in all_files:
                if f.get('asset_request_id') == asset_request_obj.id:
                    relevant_files.append(f)
            return relevant_files
        return []

    def get_quotes(self, asset_request_obj):
        all_quotes = self.context.get('request_quotes')
        if all_quotes:
            relevant_quotes = []
            for quote in all_quotes:
                if quote.get('asset_request_id') == asset_request_obj.id:
                    relevant_quotes.append(quote)
            return relevant_quotes
        return []

    def get_has_delivery_cost(self, asset_request_obj):
        all_deliveries = self.context.get('deliveries')
        if asset_request_obj.id in all_deliveries:
            return True
        return False

    class Meta:
        model = AssetRequestModel
        fields = "__all__"

class FullAssetRequestSerializer(serializers.ModelSerializer):
    asset_type = serializers.SlugRelatedField(read_only=True, source='equipment.asset_type', slug_field='name')
    model_number = serializers.SlugRelatedField(read_only=True, source='equipment', slug_field='model_number')
    justification = serializers.SlugRelatedField(slug_field='name',read_only=True)
    equipment_type = EquipmentTypeSerializer(source='equipment',read_only=True)
    business_unit = serializers.SlugRelatedField(slug_field='name', read_only=True)
    cost_centre = serializers.SlugRelatedField(read_only=True, slug_field='name')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    class Meta:
        model = AssetRequestModel
        fields = '__all__'

class AssetRequestHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetRequestModelHistory
        fields = "__all__"

class AssetRequestFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetRequestFile
        fields = "__all__"

class LightAssetRequestFileSerializer(serializers.ModelSerializer):
    vendor = serializers.SerializerMethodField()
    asset_request = serializers.SerializerMethodField()

    def get_vendor(self, ar_file_obj):
        vendors = self.context.get("all_vendors")
        for vendor in vendors:
            if ar_file_obj.get("vendor_id") == vendor.get("vendor_id"):
                return vendor
        return None

    def get_asset_request(self, maint_file_obj):
        return maint_file_obj.get("asset_request_id")

    class Meta:
        model = AssetRequestFile
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class ApprovedVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovedVendorsModel
        fields = "__all__"

class LightApprovedVendorSerializer(serializers.ModelSerializer):
    department_name = serializers.SlugRelatedField(read_only=True, source='vendor_department', slug_field='name')
    task_name = serializers.SlugRelatedField(read_only=True, source='vendor_task', slug_field='name')
    class Meta:
        model = ApprovedVendorsModel
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class ApprovedVendorDepartmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovedVendorDepartments
        fields = "__all__"

class ApprovedVendorTasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovedVendorTasks
        fields = "__all__"

class AssetDisposalSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        if validated_data.get('potential_vendor_ids') is None:
            validated_data['status'] = AssetDisposalModel.awaiting_approval
        return AssetDisposalModel.objects.create(**validated_data)

    class Meta:
        model = AssetDisposalModel
        fields = "__all__"


class LightAssetDisposalSerializer(serializers.ModelSerializer):
    asset_type = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type.asset_type', slug_field='name')
    manufacturer = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type.manufacturer', slug_field='name')
    model_number = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type', slug_field='model_number')
    engine = serializers.SlugRelatedField(read_only=True, source='VIN', slug_field='engine')
    fuel_type = serializers.SlugRelatedField(read_only=True, source='VIN.fuel', slug_field='name')
    original_location = serializers.SlugRelatedField(read_only=True, source='VIN.original_location', slug_field='location_name')
    current_location = serializers.SlugRelatedField(read_only=True, source='VIN.current_location', slug_field='location_name')
    disposal_location = serializers.SlugRelatedField(read_only=True, source='location', slug_field='location_name')
    vendor_name = serializers.SlugRelatedField(read_only=True, source='vendor', slug_field='vendor_name')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    files = serializers.SerializerMethodField()
    refurbish_work_order = serializers.SerializerMethodField()
    # quotes = serializers.SerializerMethodField()
    # has_delivery_cost = serializers.SerializerMethodField()

    def get_files(self, disposal_obj):
        all_files = self.context.get('disposal_files')
        if all_files:
            relevant_files = []
            for f in all_files:
                if f.get('disposal_id') == disposal_obj.id:
                    relevant_files.append(f)
            return relevant_files
        return []

    def get_refurbish_work_order(self, disposal_obj):
        all_refurbish_work_orders = self.context.get('refurbish_work_orders')
        if all_refurbish_work_orders:
            for refurbishment in all_refurbish_work_orders:
                if refurbishment['disposal__custom_id'] == disposal_obj.custom_id:
                    return refurbishment['work_order']
        return None

    def get_quotes(self, disposal_obj):
        all_quotes = self.context.get('request_quotes')
        if all_quotes:
            relevant_quotes = []
            for quote in all_quotes:
                if quote.get('disposal_request_id') == disposal_obj.id:
                    relevant_quotes.append(quote)
            return relevant_quotes
        return []

    def get_has_delivery_cost(self, disposal_obj):
        all_deliveries = self.context.get('deliveries')
        if disposal_obj.id in all_deliveries:
            return True
        return False

    class Meta:
        model = AssetDisposalModel
        fields = "__all__"


class AssetDisposalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetDisposalModelHistory
        fields = "__all__"


class AssetDisposalFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetDisposalFile
        fields = "__all__"

class LightAssetDisposalFileSerializer(serializers.ModelSerializer):
    vendor = serializers.SerializerMethodField()
    disposal = serializers.SerializerMethodField()

    def get_vendor(self, disposal_file_obj):
        vendors = self.context.get("all_vendors")
        for vendor in vendors:
            if disposal_file_obj.get("vendor_id") == vendor.get("vendor_id"):
                return vendor
        return None

    def get_disposal(self, disposal_file_obj):
        return disposal_file_obj.get("disposal_id")

    class Meta:
        model = AssetDisposalFile
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class AccidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccidentModel
        fields = "__all__"


class LightAccidentSerializer(serializers.ModelSerializer):
    asset_type = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type.asset_type', slug_field='name')
    business_unit = serializers.SlugRelatedField(read_only=True, source='VIN.department', slug_field='name')
    original_location = serializers.SlugRelatedField(read_only=True, source='VIN.original_location', slug_field='location_name')
    current_location = serializers.SlugRelatedField(read_only=True, source='VIN.current_location', slug_field='location_name')
    accident_location = serializers.SlugRelatedField(read_only=True, source='location', slug_field='location_name')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    files = serializers.SerializerMethodField()
    unit_number=serializers.SerializerMethodField()
    cost_centre = serializers.SlugRelatedField(read_only=True,source='VIN.cost_centre',slug_field='name')
    
    def get_unit_number(self, incident_obj):
        return incident_obj.VIN.unit_number

    def get_files(self, accident_obj):
        all_files = self.context.get('accident_files')
        if all_files:
            relevant_files = []
            for f in all_files:
                if f.get('accident_id') == accident_obj.accident_id:
                    relevant_files.append(f)
            return relevant_files
        return []

    class Meta:
        model = AccidentModel
        fields = "__all__"

# TODO: seems to be unused. remove?

"""
class FullAccidentSerializer(serializers.ModelSerializer):
    asset = AssetModelSerializer(read_only=True, source='VIN')
    asset_type = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type.asset_type', slug_field='name')
    business_unit = serializers.SlugRelatedField(read_only=True, source='VIN.department', slug_field='name')
    original_location = serializers.SlugRelatedField(read_only=True, source='VIN.original_location', slug_field='location_name')
    current_location = serializers.SlugRelatedField(read_only=True, source='VIN.current_location', slug_field='location_name')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    class Meta:
        model = AccidentModel
        fields = "__all__"
"""


class AccidentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccidentFileModel
        fields = "__all__"


class AccidentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccidentModelHistory
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class RepairSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairsModel
        fields = "__all__"


class LightRepairSerializer(serializers.ModelSerializer):
    vendor_name = serializers.SlugRelatedField(read_only=True, source='vendor', slug_field='vendor_name')
    asset_type = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type.asset_type', slug_field='name')
    manufacturer = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type.manufacturer', slug_field='name')
    model_number = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type', slug_field='model_number')
    engine = serializers.SlugRelatedField(read_only=True, source='VIN', slug_field='engine')
    fuel_type = serializers.SlugRelatedField(read_only=True, source='VIN.fuel', slug_field='name')
    business_unit = serializers.SlugRelatedField(read_only=True, source='VIN.department', slug_field='name')
    original_location = serializers.SlugRelatedField(read_only=True, source='VIN.original_location', slug_field='location_name')
    current_location = serializers.SlugRelatedField(read_only=True, source='VIN.current_location', slug_field='location_name')
    repair_location = serializers.SlugRelatedField(read_only=True, source='location', slug_field='location_name')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    class_code = serializers.SerializerMethodField()
    issues = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    unit_number=serializers.SerializerMethodField()
    # quotes = serializers.SerializerMethodField()
    # has_delivery_cost = serializers.SerializerMethodField()
    
    def get_unit_number(self, repair_obj):
        return repair_obj.VIN.unit_number

    def get_class_code(self, repair_obj):
        return repair_obj.VIN.class_code

    def get_issues(self, repair_obj):
        all_issues = self.context.get('all_issues')
        if all_issues:
            relevant_issues = []
            for item in all_issues:
                if item.repair_id == repair_obj:
                    relevant_issues.append(item)

            return LightIssueSerializer(relevant_issues, many=True, context=self.context).data
        return []

    def get_files(self, repair_obj):
        all_files = self.context.get('all_repair_files')
        if all_files:
            relevant_files = []
            for f in all_files:
                if f.get('repair_id') == repair_obj.repair_id:
                    relevant_files.append(f)

            return relevant_files
        return []

    def get_quotes(self, repair_obj):
        all_quotes = self.context.get('request_quotes')
        if all_quotes:
            relevant_quotes = []
            for quote in all_quotes:
                if quote.get('repair_request_id') == repair_obj.repair_id:
                    relevant_quotes.append(quote)
            return relevant_quotes
        return []

    def get_has_delivery_cost(self, repair_obj):
        all_deliveries = self.context.get('deliveries')
        if repair_obj.repair_id in all_deliveries:
                return True
        return False

    class Meta:
        model = RepairsModel
        fields = "__all__"

class RepairFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairFile
        fields = "__all__"

class LightRepairFileSerializer(serializers.ModelSerializer):
    vendor = serializers.SerializerMethodField()
    repair = serializers.SerializerMethodField()

    def get_vendor(self, repair_file_obj):
        vendors = self.context.get("all_vendors")
        for vendor in vendors:
            if repair_file_obj.get("vendor_id") == vendor.get("vendor_id"):
                return vendor
        return None

    def get_repair(self, repair_file_obj):
        return repair_file_obj.get("repair_id")

    class Meta:
        model = RepairFile
        fields = "__all__"

class RepairsHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairsModelHistory
        fields = "__all__"

class RepairCostExportSerializer(serializers.Serializer):
    unit_number = serializers.SerializerMethodField()
    date_of_manufacture = serializers.SerializerMethodField()
    manufacturer = serializers.SerializerMethodField()
    model_number = serializers.SerializerMethodField()
    asset_type = serializers.SerializerMethodField()
    VIN = serializers.SlugRelatedField(read_only=True, slug_field='VIN')
    mileage = serializers.SlugRelatedField(read_only=True, source='VIN', slug_field='mileage')
    hours = serializers.SlugRelatedField(read_only=True, source='VIN', slug_field='hours')
    business_unit = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    work_order_date = serializers.SerializerMethodField()
    work_order_mileage = serializers.FloatField(read_only=True, source='mileage')
    work_order_hours = serializers.FloatField(read_only=True, source='hours')
    vendor_email = serializers.CharField(read_only=True)
    work_order_id = serializers.CharField(read_only=True, source='work_order')
    work_order_type = serializers.ReadOnlyField(default='repair')
    part_cost = serializers.SerializerMethodField()
    labor_cost = serializers.SerializerMethodField()
    taxes = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    description = serializers.CharField(read_only=True)

    invalid_values = [None, '']
    invalid_return = 'NA'

    def get_unit_number(self, repair_obj):
        try:
            if repair_obj.VIN.unit_number not in self.invalid_values:
                return str(repair_obj.VIN.unit_number)
        except Exception:
            return self.invalid_return

    def get_date_of_manufacture(self, repair_obj):
        try:
            if repair_obj.VIN.date_of_manufacture not in self.invalid_values:
                return str(repair_obj.VIN.date_of_manufacture)
        except Exception:
            return self.invalid_return

    def get_manufacturer(self, repair_obj):
        try:
            if repair_obj.VIN.equipment_type.manufacturer.name not in self.invalid_values:
                return str(repair_obj.VIN.equipment_type.manufacturer.name)
        except Exception:
            return self.invalid_return

    def get_model_number(self, repair_obj):
        try:
            if repair_obj.VIN.equipment_type.model_number not in self.invalid_values:
                return str(repair_obj.VIN.equipment_type.model_number)
        except Exception:
            return self.invalid_return

    def get_asset_type(self, repair_obj):
        try:
            if repair_obj.VIN.equipment_type.asset_type.name not in self.invalid_values:
                return str(repair_obj.VIN.equipment_type.asset_type.name)
        except Exception:
            return self.invalid_return

    def get_business_unit(self, repair_obj):
        try:
            if repair_obj.VIN.department.name not in self.invalid_values:
                return str(repair_obj.VIN.department.name)
        except Exception:
            return self.invalid_return

    def get_location(self, repair_obj):
        try:
            if repair_obj.location.location_name not in self.invalid_values:
                return str(repair_obj.location.location_name)
        except Exception:
            return self.invalid_return

    def get_work_order_date(self, repair_obj):
        try:
            if repair_obj.date_created not in self.invalid_values:
                return repair_obj.date_created.strftime('%Y-%m-%d')
        except Exception:
            return self.invalid_return

    def get_part_cost(self, repair_obj):
        part_costs_list = self.context.get('part_costs')
        if part_costs_list:
            total_parts_cost = 0
            for cost in part_costs_list:
                if repair_obj.repair_id == cost.get('issue__repair_id'):
                    total_parts_cost += float(cost.get('total_cost'))
                    self.mod_context(repair_obj, cost)
            return round(total_parts_cost, 2)
        return 0

    def get_labor_cost(self, repair_obj):
        labor_costs_list = self.context.get('labor_costs')
        if labor_costs_list:
            total_labor_cost = 0
            for cost in labor_costs_list:
                if repair_obj.repair_id == cost.get('issue__repair_id'):
                    total_labor_cost += float(cost.get('total_cost'))
                    self.mod_context(repair_obj, cost)
            return round(total_labor_cost, 2)
        return 0

    def get_taxes(self, repair_obj):
        taxes = self.context.get('taxes_' + str(repair_obj.repair_id))
        if taxes:
            return round(taxes, 2)
        return 0

    def get_total_cost(self, repair_obj):
        total_cost = self.context.get('total_cost_' + str(repair_obj.repair_id))
        if total_cost:
            return round(total_cost, 2)
        return 0

    def get_currency(self, repair_obj):
        return self.context.get('currency_code')

    def mod_context(self, repair_obj, cost):
        # See if taxes key/value has been established and if not --> Establish it.
        if self.context.get('taxes_' + str(repair_obj.repair_id)) is None:
            self.context['taxes_' + str(repair_obj.repair_id)] = float(cost.get('taxes'))
        # If taxes is already established --> Add to it.
        else:
            self.context['taxes_' + str(repair_obj.repair_id)] += float(cost.get('taxes'))
        # See if total_cost key/value has been established and if not --> Establish it.
        if self.context.get('total_cost_' + str(repair_obj.repair_id)) is None:
            self.context['total_cost_' + str(repair_obj.repair_id)] = float(cost.get('total_cost'))
        # If total_cost is already established --> Add to it.
        else:
            self.context['total_cost_' + str(repair_obj.repair_id)] += float(cost.get('total_cost'))
    
# --------------------------------------------------------------------------------------------------------


class InspectionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionTypeModel
        fields = "__all__"

# ----------------------------------------------------------------------------------------------------------------

class MaintenanceRequestSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        if validated_data.get('potential_vendor_ids') is None:
            validated_data['status'] = MaintenanceRequestModel.awaiting_approval
        return MaintenanceRequestModel.objects.create(**validated_data)

    class Meta:
        model = MaintenanceRequestModel
        fields = "__all__"


class LightMaintenanceRequestSerializer(serializers.ModelSerializer):
    asset_type = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type.asset_type', slug_field='name')
    manufacturer = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type.manufacturer', slug_field='name')
    model_number = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type', slug_field='model_number')
    engine = serializers.SlugRelatedField(read_only=True, source='VIN', slug_field='engine')
    fuel_type = serializers.SlugRelatedField(read_only=True, source='VIN.fuel', slug_field='name')
    inspection_type = serializers.SlugRelatedField(read_only=True, slug_field='inspection_name')
    original_location = serializers.SlugRelatedField(read_only=True, source='VIN.original_location', slug_field='location_name')
    current_location = serializers.SlugRelatedField(read_only=True, source='VIN.current_location', slug_field='location_name')
    maintenance_location = serializers.SlugRelatedField(read_only=True, source='location', slug_field='location_name')
    vendor_name = serializers.SlugRelatedField(read_only=True, slug_field='vendor_name', source='assigned_vendor')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    files = serializers.SerializerMethodField()
    unit_number=serializers.SerializerMethodField()
    # quotes = serializers.SerializerMethodField()
    # has_delivery_cost = serializers.SerializerMethodField()
    
    def get_unit_number(self, maintenance_obj):
        return maintenance_obj.VIN.unit_number

    def get_files(self, maintenance_obj):
        all_files = self.context.get('maintenance_files')
        if all_files:
            relevant_files = []
            for f in all_files:
                if f.get('maintenance_request_id') == maintenance_obj.maintenance_id:
                    relevant_files.append(f)

            return relevant_files
        return []

    def get_quotes(self, maintenance_obj):
        all_quotes = self.context.get('request_quotes')
        if all_quotes:
            relevant_quotes = []
            for quote in all_quotes:
                if quote.get('maintenance_request_id') == maintenance_obj.maintenance_id:
                    relevant_quotes.append(quote)
            return relevant_quotes
        return []

    def get_has_delivery_cost(self, maintenance_obj):
        all_deliveries = self.context.get('deliveries')
        if maintenance_obj.maintenance_id in all_deliveries:
            return True
        return False

    class Meta:
        model = MaintenanceRequestModel
        fields = "__all__"


class MaintenanceRequestHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRequestModelHistory
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationModel
        fields = "__all__"


class MaintenanceForecastRulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceForecastRules
        fields = '__all__'

class LightMaintenanceForecastRulesSerializer(serializers.ModelSerializer):
    inspection_name = serializers.SlugRelatedField(read_only=True, source='inspection_type', slug_field='inspection_name')
    original_location = serializers.SlugRelatedField(read_only=True, source='VIN.original_location', slug_field='location_name')
    current_location = serializers.SlugRelatedField(read_only=True, source='VIN.current_location', slug_field='location_name')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')

    class Meta:
        model = MaintenanceForecastRules
        fields = "__all__"

class MaintenanceFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRequestFile
        fields = "__all__"

class LightMaintenanceFileSerializer(serializers.ModelSerializer):
    vendor = serializers.SerializerMethodField()
    maintenance_request = serializers.SerializerMethodField()

    def get_vendor(self, maint_file_obj):
        vendors = self.context.get("all_vendors")
        for vendor in vendors:
            if maint_file_obj.get("vendor_id") == vendor.get("vendor_id"):
                return vendor
        return None

    def get_maintenance_request(self, maint_file_obj):
        return maint_file_obj.get("maintenance_request_id")

    class Meta:
        model = MaintenanceRequestFile
        fields = "__all__"

class MaintenanceCostExportSerializer(serializers.Serializer):
    unit_number = serializers.SerializerMethodField()
    date_of_manufacture = serializers.SerializerMethodField()
    manufacturer = serializers.SerializerMethodField()
    model_number = serializers.SerializerMethodField()
    asset_type = serializers.SerializerMethodField()
    VIN = serializers.SlugRelatedField(read_only=True, slug_field='VIN')
    mileage = serializers.SlugRelatedField(read_only=True, source='VIN', slug_field='mileage')
    hours = serializers.SlugRelatedField(read_only=True, source='VIN', slug_field='hours')
    business_unit = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    work_order_date = serializers.SerializerMethodField()
    work_order_mileage = serializers.FloatField(read_only=True, source='mileage')
    work_order_hours = serializers.FloatField(read_only=True, source='hours')
    vendor_email = serializers.CharField(read_only=True)
    work_order_id = serializers.CharField(read_only=True, source='work_order')
    work_order_type = serializers.ReadOnlyField(default='maintenance')
    part_cost = serializers.SerializerMethodField()
    labor_cost = serializers.SerializerMethodField()
    taxes = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    invalid_values = [None, '']
    invalid_return = 'NA'

    def get_unit_number(self, maintenance_obj):
        try:
            if maintenance_obj.VIN.unit_number not in self.invalid_values:
                return str(maintenance_obj.VIN.unit_number)
        except Exception:
            return self.invalid_return

    def get_date_of_manufacture(self, maintenance_obj):
        try:
            if maintenance_obj.VIN.date_of_manufacture not in self.invalid_values:
                return str(maintenance_obj.VIN.date_of_manufacture)
        except Exception:
            return self.invalid_return

    def get_manufacturer(self, maintenance_obj):
        try:
            if maintenance_obj.VIN.equipment_type.manufacturer.name not in self.invalid_values:
                return str(maintenance_obj.VIN.equipment_type.manufacturer.name)
        except Exception:
            return self.invalid_return

    def get_model_number(self, maintenance_obj):
        try:
            if maintenance_obj.VIN.equipment_type.model_number not in self.invalid_values:
                return str(maintenance_obj.VIN.equipment_type.model_number)
        except Exception:
            return self.invalid_return

    def get_asset_type(self, maintenance_obj):
        try:
            if maintenance_obj.VIN.equipment_type.asset_type.name not in self.invalid_values:
                return str(maintenance_obj.VIN.equipment_type.asset_type.name)
        except Exception:
            return self.invalid_return

    def get_business_unit(self, maintenance_obj):
        try:
            if maintenance_obj.VIN.department.name not in self.invalid_values:
                return str(maintenance_obj.VIN.department.name)
        except Exception:
            return self.invalid_return

    def get_location(self, maintenance_obj):
        try:
            if maintenance_obj.location.location_name not in self.invalid_values:
                return str(maintenance_obj.location.location_name)
        except Exception:
            return self.invalid_return

    def get_work_order_date(self, maintenance_obj):
        try:
            if maintenance_obj.date_created not in self.invalid_values:
                return maintenance_obj.date_created.strftime('%Y-%m-%d')
        except Exception:
            return self.invalid_return

    def get_description(self, maintenance_obj):
        try:
            if maintenance_obj.inspection_type.inspection_name not in self.invalid_values:
                return str(maintenance_obj.inspection_type.inspection_name)
        except Exception:
            return self.invalid_return

    def get_part_cost(self, maintenance_obj):
        part_costs_list = self.context.get('part_costs')
        if part_costs_list:
            total_parts_cost = 0
            for cost in part_costs_list:
                if maintenance_obj.maintenance_id == cost.get('maintenance'):
                    total_parts_cost += float(cost.get('total_cost'))
                    self.mod_context(maintenance_obj, cost)
            return round(total_parts_cost, 2)
        return 0

    def get_labor_cost(self, maintenance_obj):
        labor_costs_list = self.context.get('labor_costs')
        if labor_costs_list:
            total_labor_cost = 0
            for cost in labor_costs_list:
                if maintenance_obj.maintenance_id == cost.get('maintenance'):
                    total_labor_cost += float(cost.get('total_cost'))
                    self.mod_context(maintenance_obj, cost)
            return round(total_labor_cost, 2)
        return 0

    def get_taxes(self, maintenance_obj):
        taxes = self.context.get('taxes_' + str(maintenance_obj.maintenance_id))
        if taxes:
            return round(taxes, 2)
        return 0

    def get_total_cost(self, maintenance_obj):
        total_cost = self.context.get('total_cost_' + str(maintenance_obj.maintenance_id))
        if total_cost:
            return round(total_cost, 2)
        return 0

    def get_currency(self, maintenance_obj):
        return self.context.get('currency_code')

    def mod_context(self, maintenance_obj, cost):
        # See if taxes key/value has been established and if not --> Establish it.
        if self.context.get('taxes_' + str(maintenance_obj.maintenance_id)) is None:
            self.context['taxes_' + str(maintenance_obj.maintenance_id)] = float(cost.get('taxes'))
        # If taxes is already established --> Add to it.
        else:
            self.context['taxes_' + str(maintenance_obj.maintenance_id)] += float(cost.get('taxes'))
        # See if total_cost key/value has been established and if not --> Establish it.
        if self.context.get('total_cost_' + str(maintenance_obj.maintenance_id)) is None:
            self.context['total_cost_' + str(maintenance_obj.maintenance_id)] = float(cost.get('total_cost'))
        # If total_cost is already established --> Add to it.
        else:
            self.context['total_cost_' + str(maintenance_obj.maintenance_id)] += float(cost.get('total_cost'))

# ----------------------------------------------------------------------------------------------------------------

class FleetGuruSerializer(serializers.ModelSerializer):
    class Meta:
        model = FleetGuru
        fields = "__all__"

# ----------------------------------------------------------------------------------------------------------------

class ApprovalSerializer(serializers.ModelSerializer):
    approving_user = serializers.SlugRelatedField(read_only=True, slug_field='email')
    class Meta:
        model = Approval
        fields = "__all__"
        depth = 1 

class LinkedApprovalSerializer(serializers.ModelSerializer):
    asset_type = serializers.SlugRelatedField(read_only=True, source="VIN.equipment_type.asset_type", slug_field='name')
    original_location = serializers.SlugRelatedField(read_only=True, source='VIN.original_location', slug_field='location_name')
    current_location = serializers.SlugRelatedField(read_only=True, source='VIN.current_location', slug_field='location_name')
    approval_location = serializers.SlugRelatedField(read_only=True, source='location', slug_field='location_name')
    process_type = serializers.SlugRelatedField(read_only=True, source="VIN", slug_field='last_process')
    approving_user = serializers.SlugRelatedField(read_only=True, slug_field='email')
    requesting_user = serializers.SlugRelatedField(read_only=True, slug_field='email')
    class Meta:
        model = Approval
        fields = "__all__"
        #depth = 1

# ----------------------------------------------------------------------------------------------------------------

class AssetTransferSerializer(serializers.ModelSerializer):
    business_unit = serializers.SlugRelatedField(read_only=True, source='VIN.department', slug_field='name')
    destination_location = serializers.SlugRelatedField(read_only=True, slug_field='location_name')
    transfer_original_location = serializers.SlugRelatedField(read_only=True, source='original_location', slug_field='location_name')
    original_location = serializers.SlugRelatedField(read_only=True, source='VIN.original_location', slug_field='location_name')
    current_location = serializers.SlugRelatedField(read_only=True, source='VIN.current_location', slug_field='location_name')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    files = serializers.SerializerMethodField('get_files')
    approving_user=serializers.SerializerMethodField('get_approving_user')
    unit_number=serializers.SerializerMethodField()
    cost_centre=serializers.SlugRelatedField(read_only=True,source='VIN.cost_centre',slug_field='name')
    vendor_name = serializers.SlugRelatedField(read_only=True, source='vendor', slug_field='vendor_name')
    # has_delivery_cost = serializers.SerializerMethodField()
    # quotes = serializers.SerializerMethodField()

    def get_has_delivery_cost(self, transfer_obj):
        transfers_with_delivery_costs = self.context.get('transfers_with_delivery_costs')
        if transfer_obj.asset_transfer_id in transfers_with_delivery_costs:
            return True
        return False

    def get_unit_number(self, transfer_obj):
        return transfer_obj.VIN.unit_number

    def get_files(self, transfer_obj):
        all_files = self.context.get('transfer_files')
        if all_files:
            relevant_files = []
            for f in all_files:
                if f.get('transfer_id') == transfer_obj.asset_transfer_id:
                    relevant_files.append(f)

            return relevant_files
        return []
        
    def get_approving_user(self, transfer_obj):
        approvals=self.context.get('approvals')
        if approvals:
            for approval in approvals:
                if approval.get('asset_transfer_request') == transfer_obj.asset_transfer_id:
                    if approval.get('approving_user__email') is not None:
                        return approval.get('approving_user__email')
                    else:
                        return 'NA'
        else:
            return 'NA'

    def get_quotes(self, transfer_obj):
        all_quotes = self.context.get('request_quotes')
        if all_quotes:
            relevant_quotes = []
            for quote in all_quotes:
                if quote.get('transfer_request_id') == transfer_obj.asset_transfer_id:
                    relevant_quotes.append(quote)
            return relevant_quotes
        return []
    
    class Meta:
        model = AssetTransfer
        fields = "__all__"


class TransferFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferFile
        fields = "__all__"

# ----------------------------------------------------------------------------------------------------------------

class ErrorReportSerializer(serializers.ModelSerializer):
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    files = serializers.SerializerMethodField()

    def get_files(self, error_report_obj):
        all_files = self.context.get('all_files')
        if all_files:
            relevant_files = []
            for f in all_files:
                if f.get('error_report_id') == error_report_obj.error_report_id:
                    relevant_files.append(f)
            return relevant_files
        return []

    class Meta:
        model = ErrorReport
        fields = "__all__"

class ErrorReportFileSerializer(serializers.ModelSerializer):
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    class Meta:
        model = ErrorReportFile
        fields = "__all__"

# ----------------------------------------------------------------------------------------------------------------

class AssetLogSerializer(serializers.ModelSerializer):
    log_location = serializers.SlugRelatedField(read_only=True, source='location', slug_field='location_name')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    class Meta:
        model = AssetLog
        fields = "__all__"

# ----------------------------------------------------------------------------------------------------------------

class AssetFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetFile
        fields = "__all__"

# ----------------------------------------------------------------------------------------------------------------

class FuelSerializer(serializers.ModelSerializer):
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    fuel_type = serializers.SlugRelatedField(read_only=True, slug_field='name')
    currency = serializers.SlugRelatedField(read_only=True, slug_field='code')
    class Meta:
        model = FuelCost
        fields = "__all__"

    unit_number=serializers.SerializerMethodField()
    
    def get_unit_number(self, fuel_obj):
        return fuel_obj.VIN.unit_number

# --------------------------------------------------------------------------------------------------------

class FuelCostCheckSerializer(serializers.ModelSerializer):
  
    type_description=serializers.SerializerMethodField()
    
    def get_type_description(self,check):
        return check.get_human_readable_type()
  
    class Meta:
        model=FuelCostCheck
        fields="__all__"

# --------------------------------------------------------------------------------------------------------

class FuelCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelCost
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class FuelCardSerializer(serializers.ModelSerializer):
    assigned_employee = serializers.SlugRelatedField(queryset=DetailedUser.objects.all(), slug_field='email')
    issuer = serializers.SlugRelatedField(queryset=DetailedUser.objects.all(), slug_field='email')
    class Meta:
        model = FuelCard
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class LicenseSerializer(serializers.ModelSerializer):
    
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    currency = serializers.SlugRelatedField(read_only=True, slug_field='code')
    class Meta:
        model = LicenseCost
        fields = "__all__"

class LicenseCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseCost
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------
    
class LightRentalCostSerializer(serializers.ModelSerializer):
    maintenance_work_order = serializers.SlugRelatedField(read_only=True, source='maintenance', slug_field='work_order')
    repair_work_order = serializers.SlugRelatedField(read_only=True, source='repair', slug_field='work_order')
    accident_custom_id = serializers.SlugRelatedField(read_only=True, source='accident', slug_field='custom_id')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    currency = serializers.SlugRelatedField(read_only=True, slug_field='code')
    class Meta:
        model = RentalCost
        fields = "__all__"

class RentalCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalCost
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class LightLaborCostSerializer(serializers.ModelSerializer):
    maintenance_work_order = serializers.SlugRelatedField(read_only=True, source='maintenance', slug_field='work_order')
    issue_custom_id = serializers.SlugRelatedField(read_only=True, source='issue', slug_field='custom_id')
    disposal_custom_id = serializers.SlugRelatedField(read_only=True, source='disposal', slug_field='custom_id')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    currency = serializers.SlugRelatedField(read_only=True, slug_field='code')
    class Meta:
        model = LaborCost
        fields = "__all__"

class LaborCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaborCost
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class LightPartCostSerializer(serializers.ModelSerializer):
    maintenance_work_order = serializers.SlugRelatedField(read_only=True, source='maintenance', slug_field='work_order')
    issue_custom_id = serializers.SlugRelatedField(read_only=True, source='issue', slug_field='custom_id')
    disposal_custom_id = serializers.SlugRelatedField(read_only=True, source='disposal', slug_field='custom_id')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    currency = serializers.SlugRelatedField(read_only=True, slug_field='code')
    class Meta:
        model = Parts
        fields = "__all__"
        
class PartCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parts
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------   

class LightInsuranceCostSerializer(serializers.ModelSerializer):
    accident_custom_id = serializers.SlugRelatedField(read_only=True, source='accident', slug_field='custom_id')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    currency = serializers.SlugRelatedField(read_only=True, slug_field='code')
    class Meta:
        model = InsuranceCost
        fields = "__all__"

class InsuranceCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceCost
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class AcquisitionSerializer(serializers.ModelSerializer):
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    currency = serializers.SlugRelatedField(read_only=True, slug_field='code')
    class Meta:
        model = AcquisitionCost
        fields = "__all__"

class AcquisitionCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcquisitionCost
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class JobSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSpecification
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class FuelTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelType
        fields =  "__all__"

# --------------------------------------------------------------------------------------------------------

class CurrencyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields =  "__all__"

# --------------------------------------------------------------------------------------------------------

class SnapshotDailyLocationCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SnapshotDailyLocationCost
        fields = ['location',  'total_cost_fuel', 'date_created', 'currency']

# --------------------------------------------------------------------------------------------------------

class SnapshotDailyLocationCostSerializerTest(serializers.ModelSerializer):
    class Meta:
        model = SnapshotDailyLocationCost
        fields ="__all__"

# --------------------------------------------------------------------------------------------------------

class LightDeliveryCostSerializer(serializers.ModelSerializer):
    maintenance_work_order = serializers.SlugRelatedField(read_only=True, source='maintenance', slug_field='work_order')
    repair_work_order = serializers.SlugRelatedField(read_only=True, source='repair', slug_field='work_order')
    disposal_custom_id = serializers.SlugRelatedField(read_only=True, source='disposal', slug_field='custom_id')
    asset_request_custom_id = serializers.SlugRelatedField(read_only=True, source='asset_request', slug_field='custom_id')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    currency = serializers.SlugRelatedField(read_only=True, slug_field='code')
    class Meta:
        model = DeliveryCost
        fields = "__all__"

class DeliveryCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryCost
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class NotificationConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationConfiguration
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

# serializers for dailyinspections model and history

class DailyInspectionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyInspection
        fields = "__all__"

class DailyInspectionModelHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyInspectionHistory
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class RequestQuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestQuote
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------
class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = "__all__"


class LightInventorySerializer(serializers.ModelSerializer):
    created_by = serializers.SlugRelatedField(read_only=True, slug_field="email")
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field="email")
    location = serializers.SlugRelatedField(read_only=True, slug_field="location_name")

    class Meta:
        model = Inventory
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class AnnualReportSerializer(serializers.ModelSerializer):

    class Meta:
        model=AnnualReport
        fields="__all__"

class AssetFileWithReportsSerializer(AssetFileSerializer):
  
    annual_report=serializers.SerializerMethodField()
    
    def get_annual_report(self,file):
      
        for item in self.context["report_items"]:
            if item.file.file_id==file.file_id:
                return AnnualReportSerializer(item).data

        return None

    pass