from django.db import models
from .approved_vendors import ApprovedVendorsModel
from .asset_request import AssetRequestModel
from .maintenance_request import MaintenanceRequestModel
from .repairs import RepairsModel
from .asset_disposal import AssetDisposalModel
from .asset_transfer import AssetTransfer
from .DetailedUser import DetailedUser

class RequestQuote(models.Model):

    pending = "pending"
    sent = "sent"
    received = "received"
    shortlisted = "shortlisted"
    denied = "denied"

    request_quote_status = [
        (pending, "pending"),
        (sent, "sent"),
        (received, "received"),
        (shortlisted, "shortlisted"),
        (denied, "denied")
    ]

    status = models.CharField(choices=request_quote_status, max_length=50, default=pending)
    vendor = models.ForeignKey(ApprovedVendorsModel, null=True, on_delete=models.SET_NULL)
    vendor_quote_id = models.CharField(max_length=50, null=True) # The ID of the quote on the vendor side

    estimated_cost = models.FloatField(null=True)

    asset_request = models.ForeignKey(
        AssetRequestModel,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="asset_request_quote"
    )
    maintenance_request = models.ForeignKey(
        MaintenanceRequestModel,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="maintenance_quote"
    )
    repair_request = models.ForeignKey(
        RepairsModel,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="repair_quote"
    )
    disposal_request = models.ForeignKey(
        AssetDisposalModel,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="disposal_quote"
    )
    transfer_request = models.ForeignKey(
        AssetTransfer,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="transfer_quote"
    )
    approved_by = models.ForeignKey(
        DetailedUser,
        on_delete=models.PROTECT,
        null=True,
        default=None,
        related_name="request_quote_approved_by"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)