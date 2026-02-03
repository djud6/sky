from django.db import models
from .approved_vendors import ApprovedVendorsModel
from .asset_disposal import AssetDisposalModel
from .DetailedUser import DetailedUser
from .locations import LocationModel

class AssetDisposalModelHistory(models.Model):

    Complete = "complete"
    Incomplete = "incomplete"

    disposal_status_choices = [(Complete, "complete"), (Incomplete, "Incomplete")]

    Scrap = "scrap"
    Refurbished = "refurbish"
    Remarket = "remarket"

    disposal_type_choices = [(Scrap, "scrap"), (Refurbished, "refurbish"), (Remarket, "remarket")]

    disposal_history_id = models.AutoField(primary_key=True)
    disposal = models.ForeignKey(AssetDisposalModel, null=True, on_delete=models.CASCADE)
    custom_id = models.CharField(max_length=100, default="company_name-d-id")

    status = models.CharField(choices=disposal_status_choices, max_length=50, default=Incomplete)
    vendor = models.ForeignKey(ApprovedVendorsModel, on_delete=models.SET_NULL, blank=True, null=True)
    disposal_type = models.CharField(choices=disposal_type_choices, max_length=50, default=Scrap)
    estimated_pickup_date = models.DateTimeField(blank=True, null=True)
    vendor_contacted_date = models.DateTimeField(blank=True, null=True)
    accounting_contacted_date = models.DateTimeField(blank=True, null=True)
    available_pickup_date = models.DateTimeField(blank=True, null=True)

    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='asset_disposal_history_modified_by')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.disposal)