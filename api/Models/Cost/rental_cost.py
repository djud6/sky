from django.db import models
from ..DetailedUser import DetailedUser
from .currency import Currency
from ..asset_model import AssetModel
from ..accident_report import AccidentModel
from ..maintenance_request import MaintenanceRequestModel
from ..repairs import RepairsModel
from ..locations import LocationModel

class RentalCost(models.Model):

    VIN = models.ForeignKey(AssetModel, null=True, on_delete=models.SET_NULL, related_name='rental_cost_vin')
    accident = models.ForeignKey(AccidentModel, null=True, on_delete=models.SET_NULL, related_name='rental_cost_accident')
    maintenance = models.ForeignKey(MaintenanceRequestModel, null=True, on_delete=models.SET_NULL, related_name='rental_cost_maintenance')
    repair = models.ForeignKey(RepairsModel, null=True, on_delete=models.SET_NULL, related_name='rental_cost_repair')

    total_cost = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    
    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='rental_cost_created_by')
    date_created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='rental_cost_modified_by')
    date_updated = models.DateTimeField(auto_now=True)