from django.db import models
from ..DetailedUser import DetailedUser
from .currency import Currency
from ..asset_model import AssetModel
from ..accident_report import AccidentModel
from .insurance_cost import InsuranceCost
from ..locations import LocationModel

class InsuranceCostModelHistory(models.Model):

    insurance_cost = models.ForeignKey(InsuranceCost, null=True, on_delete=models.SET_NULL)

    VIN = models.ForeignKey(AssetModel, null=True, on_delete=models.SET_NULL, related_name='insurance_cost_history_vin')
    accident = models.ForeignKey(AccidentModel, null=True, on_delete=models.SET_NULL, related_name='insurance_cost_history_accident')

    deductible = models.FloatField()
    total_cost = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    
    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    date = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='insurance_cost_history_modified_by')
