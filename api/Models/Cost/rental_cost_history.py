from django.db import models
from ..DetailedUser import DetailedUser
from .currency import Currency
from ..asset_model import AssetModel
from ..accident_report import AccidentModel
from ..maintenance_request import MaintenanceRequestModel
from ..repairs import RepairsModel
from .rental_cost import RentalCost
from ..locations import LocationModel

class RentalCostModelHistory(models.Model):

    rental_cost = models.ForeignKey(RentalCost, null=True, on_delete=models.SET_NULL)

    VIN = models.ForeignKey(AssetModel, null=True, on_delete=models.SET_NULL, related_name='rental_cost_history_vin')
    accident = models.ForeignKey(AccidentModel, null=True, on_delete=models.SET_NULL, related_name='rental_cost_history_accident')
    maintenance = models.ForeignKey(MaintenanceRequestModel, null=True, on_delete=models.SET_NULL, related_name='rental_cost_history_maintenance')
    repair = models.ForeignKey(RepairsModel, null=True, on_delete=models.SET_NULL, related_name='rental_cost_history_repair')
    
    total_cost = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    
    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    date = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='rental_cost_history_modified_by')