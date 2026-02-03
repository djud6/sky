from django.db import models
from .asset_model import AssetModel
from .locations import LocationModel
from .DetailedUser import DetailedUser
from .asset_disposal import AssetDisposalModel


class AssetTransfer(models.Model):

    not_applicable = "not applicable"

    awaiting_approval = "awaiting approval"
    approved = "approved"
    awaiting_transfer = "awaiting transfer"
    in_transit = "in transit"
    delivered = "delivered"
    denied = "denied"
    cancelled = "cancelled"

    transfer_status_choices = [(awaiting_approval, "awaiting approval"), (approved, "approved"), (awaiting_transfer, "awaiting transfer"), 
                                (in_transit, "in transit"), (delivered, "delivered"), (denied, "denied"), (cancelled,"cancelled")]

    # condition choices
    good = "good"
    average = "average"
    poor = "poor"
    condition_choices = [(good, "good"), (average, "average"), (poor, "poor"), (not_applicable, "not applicable")]

    asset_transfer_id = models.AutoField(primary_key=True)
    custom_id = models.CharField(max_length=100, default="company_name-t-id")

    VIN = models.ForeignKey(AssetModel, on_delete=models.PROTECT)
    original_location = models.ForeignKey(LocationModel, null=True, on_delete=models.SET_NULL, related_name='transfer_original_location')
    destination_location = models.ForeignKey(LocationModel, null=True, on_delete=models.SET_NULL, related_name='transfer_destination_location')
    disposal = models.ForeignKey(AssetDisposalModel, null=True, on_delete=models.SET_NULL)

    justification = models.TextField(max_length=10000, default='NA')
    status = models.CharField(choices=transfer_status_choices, max_length=50, default=awaiting_approval)
    pickup_date = models.DateField(null=True)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    interior_condition = models.CharField(choices=condition_choices, max_length=50, default=not_applicable)
    interior_condition_details = models.TextField(null=True, default=None)
    exterior_condition = models.CharField(choices=condition_choices, max_length=50, default=not_applicable)
    exterior_condition_details = models.TextField(null=True)
    mileage = models.FloatField(max_length=50, default=-1)
    hours = models.FloatField(max_length=50, default=-1)

    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='asset_transfer_created_by')
    date_created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='asset_transfer_modified_by')
    date_modified = models.DateTimeField(auto_now=True)