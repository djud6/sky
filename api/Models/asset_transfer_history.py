from django.db import models
from .locations import LocationModel
from .DetailedUser import DetailedUser
from .asset_transfer import AssetTransfer
from .asset_disposal import AssetDisposalModel

class AssetTransferModelHistory(models.Model):

    asset_transfer_history_id = models.AutoField(primary_key=True)
    asset_transfer = models.ForeignKey(AssetTransfer, on_delete=models.CASCADE)
    custom_id = models.CharField(max_length=100, default="company_name-t-id")

    original_location = models.ForeignKey(LocationModel, null=True, on_delete=models.SET_NULL, related_name='transfer_history_original_location')
    destination_location = models.ForeignKey(LocationModel, null=True, on_delete=models.SET_NULL, related_name='transfer_history_destination_location')
    disposal = models.ForeignKey(AssetDisposalModel, null=True, on_delete=models.SET_NULL)

    justification = models.TextField(max_length=10000, default='NA')
    status = models.CharField(max_length=50)
    pickup_date = models.DateField(null=True)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    interior_condition = models.CharField(max_length=50, null=True)
    interior_condition_details = models.TextField(null=True)
    exterior_condition = models.CharField(max_length=50, null=True)
    exterior_condition_details = models.TextField(null=True)
    mileage = models.FloatField(max_length=50, default=-1)
    hours = models.FloatField(max_length=50, default=-1)

    date = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='asset_transfer_history_modified_by')