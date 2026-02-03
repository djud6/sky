from django.db import models
from .asset_type import AssetTypeModel
from .asset_manufacturer import AssetManufacturerModel
from .fuel_type import FuelType
from .DetailedUser import DetailedUser

class EquipmentTypeModel(models.Model):
    equipment_type_id = models.AutoField(primary_key=True)
    model_number = models.CharField(max_length=100, null=True, blank=True)
    asset_type = models.ForeignKey(AssetTypeModel, null=True, on_delete=models.SET_NULL)
    manufacturer = models.ForeignKey(AssetManufacturerModel, null=True, on_delete=models.SET_NULL)
    fuel = models.ForeignKey(FuelType, null=True, on_delete=models.SET_NULL)
    engine = models.CharField(max_length=50, null=True, blank=True)
    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='equipment_type_created_by')
    date_created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='equipment_type_modified_by')
    date_modified = models.DateTimeField(auto_now=True)
    fuel_tank_capacity = models.FloatField(null=True)
    fuel_tank_capacity_unit = models.CharField(null=True, max_length=50)

    def __str__(self):
        return self.model_number
