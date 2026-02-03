from django.db import models
from .asset_model import AssetModel
from .inspection_type import InspectionTypeModel
from .DetailedUser import DetailedUser
from .locations import LocationModel
from .engine import EngineModel

class MaintenanceForecastRules(models.Model):

    custom_id = models.CharField(max_length=100, default="company_name-mfr-id")

    VIN = models.ForeignKey(AssetModel, on_delete=models.PROTECT)
    location = models.ForeignKey(LocationModel, on_delete=models.PROTECT)
    inspection_type = models.ForeignKey(InspectionTypeModel, on_delete=models.PROTECT)
    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='maintenance_forcast_rule_created_by')
    date_created = models.DateField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='maintenance_forcast_rule_modified_by')
    date_updated = models.DateField(auto_now=True)
    hour_cycle = models.FloatField(default=-1)
    mileage_cycle = models.FloatField(default=-1)
    time_cycle = models.FloatField(default=-1)
    linked_engine = models.ForeignKey(EngineModel, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.VIN)