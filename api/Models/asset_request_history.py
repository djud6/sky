from django.db import models
from .business_unit import BusinessUnitModel
from .equipment_type import EquipmentTypeModel
from .asset_request_justification import AssetRequestJustificationModel
from .asset_request import AssetRequestModel
from .DetailedUser import DetailedUser
from .approved_vendors import ApprovedVendorsModel
from .locations import LocationModel
from .asset_model import AssetModel


class AssetRequestModelHistory(models.Model):

    asset_request_history_id = models.AutoField(primary_key=True)
    asset_request = models.ForeignKey(AssetRequestModel, on_delete=models.CASCADE)
    custom_id = models.CharField(max_length=100, default="company_name-ar-id")

    business_unit = models.ForeignKey(BusinessUnitModel, null=True, on_delete=models.SET_NULL)
    equipment = models.ForeignKey(EquipmentTypeModel, null=True, on_delete=models.SET_NULL)
    date_required = models.DateTimeField()
    estimated_delivery_date = models.DateTimeField(null=True)
    justification = models.ForeignKey(AssetRequestJustificationModel, null=True, on_delete=models.SET_NULL)
    nonstandard_description = models.TextField(null=True)
    vendor_email = models.CharField(max_length=100, default="NA")
    vendor = models.ForeignKey(ApprovedVendorsModel, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=100, default="NA")

    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)

    VIN = models.ForeignKey(AssetModel, on_delete=models.SET_NULL, null=True, related_name="asset_request_history_vin")

    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name="asset_request_history_modified_by")
    date = models.DateTimeField(auto_now_add=True)
    
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return str(self.business_unit)
