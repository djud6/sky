from enum import Enum, auto

from django.db import models

from .DetailedUser import DetailedUser
from .asset_model import AssetModel
from .asset_daily_checks import AssetDailyChecksModel
from .maintenance_request import MaintenanceRequestModel
from .repairs import RepairsModel


class EngineModel(models.Model):
    engine_id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=100)
    hours = models.FloatField(max_length=50, default=-1)
    daily_average_hours = models.FloatField(default=0)

    VIN = models.ForeignKey(AssetModel, on_delete=models.PROTECT)

    def __str__(self):
        return f"EngineModel (engine id: {self.engine_id}, asset: {self.VIN}, name: {self.name}, hours: {self.hours})"


class EngineHistoryAction(Enum):
    Create = auto()
    Update = auto()
    Delete = auto()

    def __str__(self):
        return self.name

    def get_verb(self):
        if self == EngineHistoryAction.Create:
            return "created"
        if self == EngineHistoryAction.Update:
            return "updated"
        if self == EngineHistoryAction.Delete:
            return "removed"


class EngineHistoryModel(models.Model):
    engine_history_id = models.AutoField(primary_key=True)

    engine_id = models.ForeignKey(EngineModel, null=True, on_delete=models.SET_NULL)
    updated_name = models.CharField(max_length=100, null=True)
    updated_hours = models.FloatField(max_length=50, default=-1, null=True)

    action = models.CharField(max_length=20)
    date = models.DateTimeField(auto_now=True)
    responsible_user = models.ForeignKey(DetailedUser, on_delete=models.PROTECT)

    responsible_daily_check = models.ForeignKey(AssetDailyChecksModel, on_delete=models.PROTECT, null=True)
    responsible_maintenance = models.ForeignKey(MaintenanceRequestModel, on_delete=models.PROTECT, null=True)
    responsible_repair = models.ForeignKey(RepairsModel, on_delete=models.PROTECT, null=True)

    def __str__(self):
        responsible_request = None
        if self.responsible_daily_check:
            responsible_request = f"responsible daily check: {self.responsible_daily_check}"
        elif self.responsible_maintenance:
            responsible_request = f"responsible maintenance request: {self.responsible_maintenance}"
        elif self.responsible_repair:
            responsible_request = f"responsible repair request: {self.responsible_repair}"

        return (f"EngineHistoryModel (id: {self.engine_history_id}, action: {self.action}, "
                f"user: {self.responsible_user}, name: {self.updated_name}, hours: {self.updated_hours}, "
                f"date: {self.date}, {responsible_request})")

