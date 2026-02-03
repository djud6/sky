from django.db import models
from ..Cost.currency import Currency
from ..locations import LocationModel


class SnapshotDailyLocationCost(models.Model):

    location = models.CharField(max_length=50)
    volume_fuel = models.FloatField()
    volume_unit = models.CharField(max_length=50)
    total_cost_fuel = models.FloatField()
    taxes_fuel = models.FloatField()

    deductible = models.FloatField()
    total_cost_insurance = models.FloatField()

    total_base_hours = models.FloatField()
    total_overtime_hours = models.FloatField()
    total_cost_labor = models.FloatField()
    taxes_labor = models.FloatField()

    license_registration_cost = models.FloatField()
    license_plate_renewal_cost = models.FloatField()
    total_cost_license = models.FloatField()
    taxes_license = models.FloatField()

    total_cost_parts = models.FloatField()
    taxes_parts = models.FloatField()

    total_cost_rental = models.FloatField()

    total_cost_acquisition = models.FloatField()
    taxes_acquisition = models.FloatField()

    total_cost_delivery = models.FloatField()
    taxes_delivery = models.FloatField()

    currency = models.CharField(max_length=50)
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.location)
