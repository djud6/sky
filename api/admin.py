from django.contrib import admin
from .Models.asset_model import AssetModel
from .Models.asset_issue import AssetIssueModel
from .Models.asset_daily_checks import AssetDailyChecksModel
from .Models.asset_type import AssetTypeModel
from .Models.asset_manufacturer import AssetManufacturerModel
from .Models.equipment_type import EquipmentTypeModel
from .Models.business_unit import BusinessUnitModel
from .Models.asset_request_justification import AssetRequestJustificationModel
from .Models.asset_request import AssetRequestModel
from .Models.approved_vendor_departments import ApprovedVendorDepartments
from .Models.approved_vendor_tasks import ApprovedVendorTasks
from .Models.approved_vendors import ApprovedVendorsModel
from .Models.approved_vendor_request import ApprovedVendorRequest
from .Models.asset_disposal import AssetDisposalModel
from .Models.accident_report import AccidentModel
from .Models.repairs import RepairsModel
from .Models.inspection_type import InspectionTypeModel
from .Models.maintenance_request import MaintenanceRequestModel
from .Models.maintenance_request_file import MaintenanceRequestFile

from .Models.locations import LocationModel
# Register your models here.




admin.site.register(AssetModel)
admin.site.register(AssetIssueModel)
admin.site.register(AssetDailyChecksModel)
admin.site.register(AssetTypeModel)
admin.site.register(AssetManufacturerModel)
admin.site.register(EquipmentTypeModel)
admin.site.register(BusinessUnitModel)
admin.site.register(AssetRequestJustificationModel)
admin.site.register(AssetRequestModel)
admin.site.register(ApprovedVendorDepartments)
admin.site.register(ApprovedVendorsModel)
admin.site.register(ApprovedVendorTasks)
admin.site.register(ApprovedVendorRequest)
admin.site.register(AssetDisposalModel)
admin.site.register(AccidentModel)
admin.site.register(RepairsModel)
admin.site.register(LocationModel)
admin.site.register(InspectionTypeModel)
admin.site.register(MaintenanceRequestModel)