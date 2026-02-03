from django.db import models
from .asset_model import AssetModel
from .approved_vendors import ApprovedVendorsModel
from .DetailedUser import DetailedUser
from .locations import LocationModel


class AssetDisposalModel(models.Model):

    not_applicable = "not applicable"
    unknown = "unknown"

    # disposal type choices
    scrap = "scrap"
    repurpose = "repurpose"
    company_directed_sale = "company directed sale"
    auction = "auction"
    donate = "donate"
    trade_in = "trade in"
    transfer = "transfer"
    write_off = "write-off"
    disposal_type_choices = [
        (scrap, "scrap"),
        (repurpose, "repurpose"),
        (auction, "auction"),
        (company_directed_sale, "company directed sale"),
        (donate, "donate"),
        (trade_in, "trade in"),
        (transfer, "transfer"),
        (write_off, "write-off"),
        (unknown, "unknown"),
    ]

    # condition choices
    good = "good"
    average = "average"
    poor = "poor"
    condition_choices = [(good, "good"), (average, "average"), (poor, "poor"), (not_applicable, "not applicable")]

    # reason for disposal choices
    being_replaced = "being replaced"
    operational_change = "operational change"
    location_closing = "location closing"
    unfit_for_purpose = "no longer fit for purpose"
    reason_for_disposal_choices = [
        (being_replaced, "being replaced"),
        (operational_change, "operational change"),
        (location_closing, "location closing"),
        (unfit_for_purpose, "no longer fit for purpose"),
    ]

    # reason for replacement choices
    end_of_useful_life = "end of useful life"
    accident = "accident"
    equipment_failure = "equipment failure"
    incident = "incident"
    reason_for_replacement_choices = [
        (end_of_useful_life, "end of useful life"),
        (accident, "accident"),
        (equipment_failure, "equipment failure"),
        (not_applicable, "not applicable"),
        (incident, "incident"),
    ]

    # status
    awaiting_approval = "awaiting approval"
    approved = "approved"
    denied = "denied"
    awaiting_pickup = "awaiting pickup"
    in_transit = "in transit"
    at_vendor = "at vendor"
    in_progress = "in progress"
    complete = "complete"
    cancelled = "cancelled"

    disposal_status_choices = [
        (awaiting_approval, "awaiting approval"),
        (approved, "approved"),
        (denied, "denied"),
        (awaiting_pickup, "awaiting pickup"),
        (in_transit, "in transit"),
        (at_vendor, "at vendor"),
        (in_progress, "in progress"),
        (complete, "complete"),
        (cancelled, "cancelled"),
    ]

    custom_id = models.CharField(max_length=100, default="company_name-d-id")

    VIN = models.ForeignKey(AssetModel, on_delete=models.PROTECT)
    vendor = models.ForeignKey(ApprovedVendorsModel, on_delete=models.SET_NULL, blank=True, null=True)
    disposal_type = models.CharField(choices=disposal_type_choices, max_length=50, default=unknown)
    estimated_pickup_date = models.DateTimeField(blank=True, null=True)
    vendor_contacted_date = models.DateTimeField(blank=True, null=True)
    accounting_contacted_date = models.DateTimeField(blank=True, null=True)
    available_pickup_date = models.DateTimeField(blank=True, null=True)
    interior_condition = models.CharField(choices=condition_choices, max_length=50, default=not_applicable)
    interior_condition_details = models.TextField()
    exterior_condition = models.CharField(choices=condition_choices, max_length=50, default=not_applicable)
    exterior_condition_details = models.TextField()
    disposal_reason = models.CharField(choices=reason_for_disposal_choices, max_length=50, default=unknown)
    replacement_reason = models.CharField(choices=reason_for_replacement_choices, max_length=50, default=not_applicable)
    is_stripped = models.BooleanField(default=False)
    refurbished = models.BooleanField(default=False)
    vendor_email = models.CharField(max_length=50, blank=True, default=not_applicable)
    status = models.CharField(choices=disposal_status_choices, max_length=50, default=awaiting_approval)

    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)

    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name="asset_disposal_created_by")
    date_created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name="asset_disposal_modified_by")
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.VIN)
