from django.db import models
from ..DetailedUser import DetailedUser
from .currency import Currency
from ..fuel_type import FuelType
from ..locations import LocationModel
from ..asset_model import AssetModel
from .fuel_cost import FuelCost

class FuelCostModelHistory(models.Model):

    fuel_cost = models.ForeignKey(FuelCost, null=True, on_delete=models.SET_NULL)
    VIN = models.ForeignKey(AssetModel, null=True, on_delete=models.SET_NULL)
    fuel_type = models.ForeignKey(FuelType, null=True, on_delete=models.SET_NULL)
    volume = models.FloatField()
    volume_unit = models.CharField(max_length=50)
    total_cost = models.FloatField()
    taxes = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    
    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    date = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='fuel_cost_history_modified_by')