from django.db import models
from .DetailedUser import DetailedUser
from .asset_request import AssetRequestModel
from .maintenance_request import MaintenanceRequestModel
from .repairs import RepairsModel
from .approval import Approval
from .asset_transfer import AssetTransfer
from .locations import LocationModel

class ApprovalModelHistory(models.Model):

    approval_history_id = models.AutoField(primary_key=True)
    approval = models.ForeignKey(Approval, on_delete=models.CASCADE)
    requesting_user = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, related_name='approval_history_requesting_user')
    approving_user = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, related_name='approval_history_approving_user')
    asset_request = models.ForeignKey(AssetRequestModel, null=True, default=None, on_delete=models.SET_NULL)
    maintenance_request = models.ForeignKey(MaintenanceRequestModel, null=True, default=None, on_delete=models.SET_NULL)
    repair_request = models.ForeignKey(RepairsModel, null=True, default=None, on_delete=models.SET_NULL)
    asset_transfer_request = models.ForeignKey(AssetTransfer, null=True, default=None, on_delete=models.SET_NULL)
    title = models.CharField(max_length=100, default="NA")
    description = models.TextField(max_length=10000, default="NA")
    deny_reason = models.TextField(max_length=10000, default="NA")
    is_approved = models.BooleanField(null=True, default=None)
    accident_summary = models.TextField(null=True, blank=True)

    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    date = models.DateTimeField(auto_now_add=True)

    

