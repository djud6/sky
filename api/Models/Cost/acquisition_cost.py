from django.db import models
from ..DetailedUser import DetailedUser
from .currency import Currency
from ..asset_model import AssetModel
from ..locations import LocationModel

class AcquisitionCost(models.Model):

    VIN = models.ForeignKey(AssetModel, null=True, on_delete=models.SET_NULL)

    total_cost = models.FloatField()
    taxes = models.FloatField()
    administrative_cost = models.FloatField()
    misc_cost = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    
    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='acquisition_cost_created_by')
    date_created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='acquisition_cost_modified_by')
    date_updated = models.DateTimeField(auto_now=True)