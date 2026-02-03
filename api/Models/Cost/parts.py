from django.db import models
from ..maintenance_request import MaintenanceRequestModel
from ..asset_issue import AssetIssueModel
from ..asset_disposal import AssetDisposalModel
from ..DetailedUser import DetailedUser
from .currency import Currency
from ..asset_model import AssetModel
from ..locations import LocationModel

class Parts(models.Model):

    maintenance = models.ForeignKey(MaintenanceRequestModel, null=True, on_delete=models.SET_NULL)
    issue = models.ForeignKey(AssetIssueModel, null=True, on_delete=models.SET_NULL)
    disposal = models.ForeignKey(AssetDisposalModel, null=True, on_delete=models.SET_NULL)

    part_number = models.CharField(max_length=100)
    part_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.FloatField()
    taxes = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    total_cost = models.FloatField()

    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='parts_created_by')
    date_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='parts_modified_by')

