from django.db import models
from .DetailedUser import DetailedUser
from .business_unit import BusinessUnitModel

class FuelCard(models.Model):

    card_id = models.AutoField(primary_key=True)
    business_unit = models.ForeignKey(BusinessUnitModel, null=True, on_delete=models.SET_NULL)
    assigned_employee = models.ForeignKey(DetailedUser, null=True, related_name='assigned_fuel_cards', on_delete=models.SET_NULL, to_field="email")
    issuer = models.ForeignKey(DetailedUser, null=True, related_name='issued_fuel_cards', on_delete=models.SET_NULL, to_field="email")
    expiration = models.DateField(null=True)
    is_active = models.BooleanField(default=True)