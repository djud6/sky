from django.db import models
from .asset_model import AssetModel
from .DetailedUser import DetailedUser
from .asset_request import AssetRequestModel
from .maintenance_request import MaintenanceRequestModel
from .repairs import RepairsModel
from .asset_transfer import AssetTransfer
from .locations import LocationModel

class Approval(models.Model):

    approval_id = models.AutoField(primary_key=True)
    VIN = models.ForeignKey(AssetModel, on_delete=models.PROTECT)
    requesting_user = models.ForeignKey(DetailedUser, null=True, on_delete=models.PROTECT, related_name='approval_requesting_user')
    approving_user = models.ForeignKey(DetailedUser, null=True, on_delete=models.PROTECT, related_name='approval_approving_user')
    asset_request = models.ForeignKey(AssetRequestModel, null=True, default=None, on_delete=models.SET_NULL)
    maintenance_request = models.ForeignKey(MaintenanceRequestModel, null=True, default=None, on_delete=models.SET_NULL)
    repair_request = models.ForeignKey(RepairsModel, null=True, default=None, on_delete=models.SET_NULL)
    asset_transfer_request = models.ForeignKey(AssetTransfer, null=True, default=None, on_delete=models.SET_NULL)
    title = models.CharField(max_length=100, default="NA")
    description = models.TextField(max_length=10000, default="NA")
    deny_reason = models.TextField(max_length=10000, default="NA")
    is_approved = models.BooleanField(null=True, default=None)

    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True) 
    

