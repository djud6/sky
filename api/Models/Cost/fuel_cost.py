from django.db import models
from ..DetailedUser import DetailedUser
from .currency import Currency
from ..fuel_type import FuelType
from ..asset_model import AssetModel
from ..locations import LocationModel

class FuelCost(models.Model):

    liter = "liter"
    gallon = "gallon"
    kg = "kg" # kilograms
    lb = "lb" # pounds
    kWh = "kWh" # kilowatt-Hours
    SCM = "SCM" # standard cubic meter
    SCF = "SCF" # standard cubic foot

    volume_unit_choices = [(liter, "liter"), (gallon, "gallon"), (kg, "kg"), (lb, "lb"), (kWh, "kWh"), (SCM, "SCM"), (SCF, "SCF")]

    VIN = models.ForeignKey(AssetModel, null=True, on_delete=models.SET_NULL)
    fuel_type = models.ForeignKey(FuelType, null=True, on_delete=models.SET_NULL)

    volume = models.FloatField()
    volume_unit = models.CharField(choices=volume_unit_choices, max_length=50)
    total_cost = models.FloatField()
    taxes = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    
    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='fuel_cost_created_by')
    date_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='fuel_cost_modified_by')

    flagged=models.BooleanField(default=False)