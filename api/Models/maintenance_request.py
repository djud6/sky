from django.db import models
from .asset_model import AssetModel
from .inspection_type import InspectionTypeModel
from .approved_vendors import ApprovedVendorsModel
from .locations import LocationModel
from .DetailedUser import DetailedUser


class MaintenanceRequestModel(models.Model):

    # status
    awaiting_approval = "awaiting approval"
    approved = "approved"
    denied = "denied"
    in_transit = "in transit"
    at_vendor = "at vendor"
    in_progress = "in progress"
    complete = "complete"
    delivered = "delivered"
    cancelled = "cancelled"

    maintenance_status_choices = [
        (awaiting_approval, "awaiting approval"),
        (approved, "approved"),
        (denied, "denied"),
        (in_transit, "in transit"),
        (at_vendor, "at vendor"),
        (in_progress, "in progress"),
        (complete, "complete"),
        (delivered, "delivered"),
        (cancelled, "cancelled"),
    ]

    incomplete_status_values = [awaiting_approval, approved, in_transit, at_vendor, in_progress, complete]
    complete_status_values = [denied, delivered, cancelled]

    maintenance_id = models.AutoField(primary_key=True)
    work_order = models.CharField(max_length=100, default="Company_name-m-id")

    VIN = models.ForeignKey(AssetModel, on_delete=models.PROTECT)
    inspection_type = models.ForeignKey(InspectionTypeModel, on_delete=models.PROTECT)
    assigned_vendor = models.ForeignKey(ApprovedVendorsModel, null=True, on_delete=models.SET_NULL)
    location = models.ForeignKey(LocationModel, null=True, on_delete=models.PROTECT)
    in_house = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name="maintenance_created_by"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(
        DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name="maintenance_modified_by"
    )
    date_updated = models.DateTimeField(auto_now=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    estimated_delivery_date = models.DateTimeField(blank=True, null=True)
    requested_delivery_date = models.DateTimeField(blank=True, null=True)
    vendor_contacted_date = models.DateTimeField(blank=True, null=True)
    available_pickup_date = models.DateTimeField(blank=True, null=True)
    vendor_email = models.CharField(max_length=100, blank=True, default="NA")
    mileage = models.FloatField(max_length=50, default=-1)
    hours = models.FloatField(max_length=50, default=-1)
    status = models.CharField(choices=maintenance_status_choices, max_length=50, default=approved)

    def __str__(self):
        return str(self.VIN)
