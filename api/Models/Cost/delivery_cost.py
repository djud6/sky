from api.Models.asset_disposal import AssetDisposalModel
from api.Models.asset_request import AssetRequestModel
from api.Models.repairs import RepairsModel
from api.Models.maintenance_request import MaintenanceRequestModel
from django.db import models
from ..DetailedUser import DetailedUser
from .currency import Currency
from ..locations import LocationModel

class DeliveryCost(models.Model):

    maintenance = models.ForeignKey(MaintenanceRequestModel, null=True, on_delete=models.SET_NULL)
    repair = models.ForeignKey(RepairsModel, null=True, on_delete=models.SET_NULL)
    disposal = models.ForeignKey(AssetDisposalModel, null=True, on_delete=models.SET_NULL)
    asset_request = models.ForeignKey(AssetRequestModel, null=True, on_delete=models.SET_NULL)

    price = models.FloatField()
    taxes = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    total_cost = models.FloatField()
    
    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='delivery_cost_created_by')
    date_created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='delivery_cost_modified_by')
    date_updated = models.DateTimeField(auto_now=True)