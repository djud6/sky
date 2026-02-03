from django.db import models
from .asset_model import AssetModel
from .approved_vendors import ApprovedVendorsModel
from .asset_disposal import AssetDisposalModel
from .locations import LocationModel
from .DetailedUser import DetailedUser


class RepairsModel(models.Model):

    # status
    approved = "approved"
    at_vendor = "at vendor"
    awaiting_approval = "awaiting approval"
    awaiting_repair = "awaiting repair"
    cancelled = "cancelled"
    complete = "complete"
    delivered = "delivered"
    denied = "denied"
    in_progress = "in progress"
    in_transit = "in transit"
    schedule = "scheduled"
    scrapped = "scrapped"
    sold = "sold"
    spare = "spare"
    under_repair = "under repair"
    unassigned = "unassigned"
    waiting_for_pickup = "waiting for pickup"
    waiting_on_parts = "waiting on parts"

    repair_status_choices = [
        (approved, "Approved"),
        (at_vendor, "At Vendor"),
        (awaiting_approval, "Awaiting Approval"),
        (awaiting_repair, "Awaiting Repair"),
        (cancelled, "Cancelled"),
        (complete, "Complete"),
        (delivered, "Delivered"),
        (denied, "Denied"),
        (in_progress, "In Progress"),
        (in_transit, "In Transit"),
        (schedule, "Scheduled"),
        (scrapped, "Scrapped"),
        (sold, "Sold"),
        (spare, "Spare"),
        (under_repair, "Under Repair"),
        (unassigned, "Unassigned"),
        (waiting_for_pickup, "Waiting for Pickup"),
        (waiting_on_parts, "Waiting on Parts"),
    ]

    incomplete_status_values = [awaiting_approval, approved, in_transit, at_vendor, under_repair, schedule, waiting_on_parts, waiting_for_pickup, in_progress, unassigned, spare, sold, scrapped, awaiting_repair]
    complete_status_values = [denied, delivered, cancelled, complete] 

    repair_id = models.AutoField(primary_key=True)
    work_order = models.CharField(max_length=100, default="Company_name-r-id")

    VIN = models.ForeignKey(AssetModel, on_delete=models.PROTECT)
    created_by = models.ForeignKey(
        DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name="repair_created_by"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(
        DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name="repair_modified_by"
    )
    date_modified = models.DateTimeField(auto_now=True)
    in_house = models.BooleanField(default=False)
    vendor = models.ForeignKey(ApprovedVendorsModel, null=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True)
    disposal = models.ForeignKey(AssetDisposalModel, null=True, on_delete=models.SET_NULL)
    is_refurbishment = models.BooleanField(default=False)
    requested_delivery_date = models.DateTimeField(blank=True, null=True)
    estimated_delivery_date = models.DateTimeField(blank=True, null=True)
    available_pickup_date = models.DateTimeField(blank=True, null=True)
    location = models.ForeignKey(LocationModel, null=True, on_delete=models.SET_NULL)
    date_completed = models.DateTimeField(blank=True, null=True)
    down_time = models.FloatField(blank=True, null=True)
    vendor_contacted_date = models.DateTimeField(blank=True, null=True)
    vendor_email = models.CharField(max_length=100, blank=True, default="NA")
    mileage = models.FloatField(max_length=50, default=-1)
    hours = models.FloatField(max_length=50, default=-1)
    is_urgent = models.BooleanField(default=False)
    status = models.CharField(choices=repair_status_choices, max_length=50, default=approved)

    def __str__(self):
        return str(self.VIN)
