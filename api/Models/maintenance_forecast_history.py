from django.db import models
from .maintenance_forecast import MaintenanceForecastRules
from .DetailedUser import DetailedUser
from .engine import EngineModel

class MaintenanceForecastRulesHistory(models.Model):

    maintenance_forecast_history_id = models.AutoField(primary_key=True)
    maintenance_forecast = models.ForeignKey(MaintenanceForecastRules, on_delete=models.CASCADE)
    custom_id = models.CharField(max_length=100, default="company_name-mfr-id")

    date = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='maintenance_rule_history_modified_by')
    hour_cycle = models.FloatField(default=-1)
    mileage_cycle = models.FloatField(default=-1)
    time_cycle = models.FloatField(default=-1)
    linked_engine = models.ForeignKey(EngineModel, null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return str(self.maintenance_forecast_history_id)