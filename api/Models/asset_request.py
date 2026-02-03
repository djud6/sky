from django.db import models
from .business_unit import BusinessUnitModel
from .cost_centre import CostCentreModel
from .equipment_type import EquipmentTypeModel
from .asset_request_justification import AssetRequestJustificationModel
from .asset_disposal import AssetDisposalModel
from .DetailedUser import DetailedUser
from .approved_vendors import ApprovedVendorsModel
from .locations import LocationModel
from .asset_model import AssetModel


class AssetRequestModel(models.Model):

    # status
    awaiting_approval = "awaiting approval"
    denied = "denied"
    approved = "approved"
    ordered = "ordered"
    built = "built"
    in_transit = "in transit"
    delivered = "delivered"
    cancelled = "cancelled"

    asset_request_status_choices = [
        (awaiting_approval, "awaiting approval"),
        (denied, "denied"),
        (approved, "approved"),
        (ordered, "ordered"),
        (built, "built"),
        (in_transit, "in transit"),
        (delivered, "delivered"),
        (cancelled, "cancelled"),
    ]

    incomplete_status_values = [awaiting_approval, approved, in_transit]
    complete_status_values = [denied, delivered, cancelled]

    custom_id = models.CharField(max_length=100, default="company_name-ar-id")

    business_unit = models.ForeignKey(BusinessUnitModel, on_delete=models.PROTECT)
    cost_centre = models.ForeignKey(CostCentreModel, on_delete=models.PROTECT, null=True)
    equipment = models.ForeignKey(EquipmentTypeModel, on_delete=models.PROTECT)
    disposal = models.ForeignKey(AssetDisposalModel, null=True, default=None, on_delete=models.PROTECT)
    date_required = models.DateTimeField()
    estimated_delivery_date = models.DateTimeField(null=True)
    justification = models.ForeignKey(AssetRequestJustificationModel, on_delete=models.PROTECT)
    nonstandard_description = models.TextField(null=True)
    vendor_email = models.CharField(max_length=100, default="NA")
    status = models.CharField(choices=asset_request_status_choices, max_length=50, default=approved)
    vendor = models.ForeignKey(ApprovedVendorsModel, null=True, on_delete=models.SET_NULL)

    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)

    VIN = models.ForeignKey(AssetModel, on_delete=models.SET_NULL, null=True, related_name="asset_request_vin")

    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name="asset_request_created_by")
    date_created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name="asset_request_modified_by")
    date_updated = models.DateTimeField(auto_now=True)

    quantity = models.IntegerField(default=1)

    def __str__(self):
        return str(self.business_unit)
