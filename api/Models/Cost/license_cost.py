from django.db import models
from ..asset_model import AssetModel
from ..DetailedUser import DetailedUser
from ..Cost.currency import Currency
from ..locations import LocationModel

class LicenseCost(models.Model):

    VIN = models.ForeignKey(AssetModel, null=True, on_delete=models.SET_NULL)

    license_registration = models.FloatField()
    taxes = models.FloatField()
    license_plate_renewal = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    total_cost = models.FloatField()

    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='license_fees_created_by')
    date_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='license_fees_modified_by')
