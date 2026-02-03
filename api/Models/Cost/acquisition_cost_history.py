from django.db import models
from ..DetailedUser import DetailedUser
from .currency import Currency
from ..asset_model import AssetModel
from .acquisition_cost import AcquisitionCost
from ..locations import LocationModel

class AcquisitionCostModelHistory(models.Model):

    acquisition_cost = models.ForeignKey(AcquisitionCost, null=True, on_delete=models.SET_NULL)
    VIN = models.ForeignKey(AssetModel, null=True, on_delete=models.SET_NULL)

    total_cost = models.FloatField()
    taxes = models.FloatField()
    administrative_cost = models.FloatField()
    misc_cost = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)

    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   
    
    date = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='acquisition_cost_history_modified_by')