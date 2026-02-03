from django.db import models
from api.Models.business_unit import BusinessUnitModel
from api.Models.locations import LocationModel
from api.Models.equipment_type import EquipmentTypeModel
from api.Models.asset_model import AssetModel
from api.Models.Company import Company
from api.Models.Cost.currency import Currency
from .fuel_type import FuelType
from .job_specification import JobSpecification
from .DetailedUser import DetailedUser

class AssetModelHistory(models.Model):
    
    Repair = "Repair"
    Accident = "Accident"
    Disposal = "Disposal"
    Maintenance = "Maintenance"
    Null = "Null"

    process_choices = [(Repair, "Repair"), (Accident, "Accident"), (Disposal, "Disposal"), (Maintenance, "Preventitive Maintenance"), (Null, None)]

    Active = "Active"
    Inop = "Inoperative"
    status_choices = [(Active, "Active"), (Inop, "Inoperative")]

    asset_history_id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    VIN = models.ForeignKey(AssetModel, null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey(AssetModel, null=True, default=None, on_delete=models.SET_NULL, related_name='asset_history_parent')
    equipment_type = models.ForeignKey(EquipmentTypeModel, null=True, on_delete=models.SET_NULL)
    company = models.ForeignKey(Company, null=True, on_delete=models.SET_NULL)
    jde_department = models.CharField(max_length=100, null=True, blank=True)
    original_location = models.ForeignKey(LocationModel, null=True, on_delete=models.SET_NULL, related_name='asset_history_original_location')
    current_location = models.ForeignKey(LocationModel, null=True, on_delete=models.SET_NULL, related_name='asset_history_current_location')
    status = models.CharField(max_length=50, choices=status_choices, default=Active, blank=True)
    unit_number = models.CharField(max_length=100, null=True, blank=True)
    license_plate = models.CharField(max_length=100, null=True, blank=True)
    department = models.ForeignKey(BusinessUnitModel, null=True, on_delete=models.SET_NULL)
    job_specification = models.ForeignKey(JobSpecification, null=True, on_delete=models.SET_NULL)
    fire_extinguisher_quantity = models.CharField(max_length=100, null=True, blank=True)
    fire_extinguisher_inspection_date = models.CharField(max_length=100, null=True, blank=True)
    path = models.CharField(max_length=300, null=True, blank=True)
    last_process = models.CharField(choices=process_choices, max_length=50, default=Null)
    hours_or_mileage = models.CharField(max_length=50)
    mileage = models.FloatField(max_length=50, default=-1)
    hours = models.FloatField(max_length=50, default=-1)
    mileage_unit = models.CharField(max_length=50, null=True, default=None)
    total_cost = models.FloatField(default=0)
    currency = models.ForeignKey(Currency, null=True, on_delete=models.SET_NULL)
    daily_average_hours = models.FloatField(default=0)
    daily_average_mileage = models.FloatField(default=0)
    replacement_hours = models.FloatField(null=True, default=0)
    replacement_mileage = models.FloatField(null=True, default=0)
    load_capacity = models.FloatField(blank=True, null=True)
    load_capacity_unit = models.CharField(max_length=50, null=True, blank=True)
    fuel = models.ForeignKey(FuelType, null=True, on_delete=models.SET_NULL)
    engine = models.CharField(max_length=50, null=True, blank=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='asset_history_modified_by')
    fuel_tank_capacity = models.FloatField(null=True)
    fuel_tank_capacity_unit = models.CharField(null=True, max_length=50)
    is_rental = models.BooleanField(null=True)
    monthly_subscription_cost = models.FloatField(null=True)
    class_code = models.CharField(max_length=50, null=True)
    asset_description = models.TextField(null=True)
    custom_fields = models.TextField(null=True)
    overdue_date_variance = models.IntegerField(default=0, null=False) #measured in days. Number of days the overdue days can be shifted
    due_soon_date_variance = models.IntegerField(default=-7, null=False) #measured in days. Number of days the due soon days can be shifted

    def __str__(self):
        return str(self.asset_history_id)
