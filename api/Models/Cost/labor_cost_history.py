from django.db import models
from ..DetailedUser import DetailedUser
from .currency import Currency
from ..maintenance_request import MaintenanceRequestModel
from ..asset_issue import AssetIssueModel
from ..asset_disposal import AssetDisposalModel
from .labor_cost import LaborCost
from ..locations import LocationModel

class LaborCostModelHistory(models.Model):

    maintenance = models.ForeignKey(MaintenanceRequestModel, null=True, on_delete=models.SET_NULL)
    issue = models.ForeignKey(AssetIssueModel, null=True, on_delete=models.SET_NULL)
    disposal = models.ForeignKey(AssetDisposalModel, null=True, on_delete=models.SET_NULL)
    labor = models.ForeignKey(LaborCost, null=True, on_delete=models.SET_NULL)
    
    base_hourly_rate = models.FloatField()
    total_base_hours = models.FloatField()
    overtime_rate = models.FloatField()
    total_overtime_hours = models.FloatField()
    taxes = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    total_cost = models.FloatField()

    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    date_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='labor_history_modified_by')