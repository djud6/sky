from django.db import models
from django.db.models.fields import related
from api.Models.business_unit import BusinessUnitModel
from api.Models.cost_centre import CostCentreModel
from api.Models.locations import LocationModel
from api.Models.equipment_type import EquipmentTypeModel
from api.Models.Company import Company
from api.Models.Cost.currency import Currency
from .fuel_type import FuelType
from .job_specification import JobSpecification
from .DetailedUser import DetailedUser
from django.core.validators import MinValueValidator,MaxValueValidator

from django.utils import timezone
from datetime import timedelta

# This is the model for the assets, primary key is VIN Number, All fields are required except Unit Number
class AssetModel(models.Model):
    
    Repair = "Repair"
    Accident = "Accident"
    Disposal = "Disposal"
    Maintenance = "Maintenance"
    Transfer = "Transfer"
    Null = "Null"
    
    Mileage = "mileage"
    Hours = "hours"
    Both = "both"
    Neither = "neither"

    kg = "kg"
    lb = "lb"

    km = "km"
    mi = "mi"

    Active = "Active"
    Inop = "Inoperative"
    Disposed = "Disposed-of"

    process_choices = [
        (Repair, "Repair"),
        (Accident, "Accident"),
        (Disposal, "Disposal"),
        (Maintenance, "Maintenance"),
        (Transfer, "Transfer"),
        (Null, None)
    ]
    hours_or_mileage_choices = [(Mileage, "mileage"), (Hours, "hours"), (Both, "both"), (Neither, "neither")]
    load_capacity_unit_choices = [(kg, "kg"), (lb, "lb")]
    mileage_unit_choices = [(km, "km"), (mi, "mi"), (Null, None)]
    status_choices = [(Active, "Active"), (Inop, "Inoperative"), (Disposed, "Disposed-of")]

    VIN = models.CharField(max_length=100, primary_key=True)
    parent = models.ForeignKey('self', null=True, default=None, on_delete=models.SET_NULL, related_name='asset_parent')
    equipment_type = models.ForeignKey(EquipmentTypeModel, null=True, on_delete=models.SET_NULL)
    company = models.ForeignKey(Company, null=True, on_delete=models.SET_NULL)
    jde_department = models.CharField(max_length=100, null=True, blank=True)
    original_location = models.ForeignKey(LocationModel, null=True, on_delete=models.SET_NULL, related_name='asset_original_location')
    current_location = models.ForeignKey(LocationModel, null=True, on_delete=models.SET_NULL, related_name='asset_current_location')
    status = models.CharField(max_length=50, choices=status_choices, default=Active, blank=True)
    aircraft_compatability = models.CharField(max_length=100, null=True, blank=True)
    unit_number = models.CharField(max_length=100, null=True, blank=True)
    license_plate = models.CharField(max_length=100, null=True, blank=True)
    date_of_manufacture = models.DateField(null=True)
    department = models.ForeignKey(BusinessUnitModel, null=True, on_delete=models.SET_NULL)
    cost_centre = models.ForeignKey(CostCentreModel, null=True, on_delete=models.SET_NULL)
    job_specification = models.ForeignKey(JobSpecification, null=True, on_delete=models.SET_NULL)
    fire_extinguisher_quantity = models.CharField(max_length=100, null=True, blank=True)
    fire_extinguisher_inspection_date = models.DateField(null=True)
    path = models.CharField(max_length=300, null=True, blank=True)
    last_process = models.CharField(choices=process_choices, max_length=50, default=Null)
    hours_or_mileage = models.CharField(choices=hours_or_mileage_choices, max_length=50, default=Neither)
    mileage = models.FloatField(max_length=50, default=-1)
    hours = models.FloatField(max_length=50, default=-1)
    mileage_unit = models.CharField(choices=mileage_unit_choices, max_length=50, null=True, default=None)
    date_in_service = models.DateField(null=True)
    total_cost = models.FloatField(default=0)
    currency = models.ForeignKey(Currency, null=True, on_delete=models.SET_NULL)
    daily_average_hours = models.FloatField(default=0)
    daily_average_mileage = models.FloatField(default=0)
    replacement_hours = models.FloatField(null=True, default=0)
    replacement_mileage = models.FloatField(null=True, default=0)
    insurance_renewal_date = models.DateField(blank=True, null=True)
    registration_renewal_date = models.DateField(blank=True, null=True)
    load_capacity = models.FloatField(blank=True, null=True)
    load_capacity_unit = models.CharField(choices=load_capacity_unit_choices, max_length=50, null=True, blank=True)
    fuel = models.ForeignKey(FuelType, null=True, on_delete=models.SET_NULL)
    
    # TODO: moving to Engine objects; this property will be obsolete eventually
    
    engine = models.CharField(max_length=50, null=True, blank=True)
    colour = models.CharField(max_length=50, default="NA")
    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='asset_created_by')
    date_created = models.DateField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='asset_modified_by')
    date_updated = models.DateTimeField(auto_now=True)
    fuel_tank_capacity = models.FloatField(null=True)
    fuel_tank_capacity_unit = models.CharField(null=True, max_length=50)
    is_rental = models.BooleanField(null=True)
    monthly_subscription_cost = models.FloatField(null=True)
    class_code = models.CharField(max_length=50, null=True)
    asset_description = models.TextField(null=True)
    custom_fields = models.TextField(null=True)
    overdue_date_variance = models.IntegerField(default=0, null=False) #measured in days. Number of days the overdue days can be shifted
    due_soon_date_variance = models.IntegerField(default=-7, null=False) #measured in days. Number of days the due soon days can be shifted
    
    lifespan_years = models.IntegerField(null=False, default=15, validators=[
        MinValueValidator(1)
    ])

    def __str__(self):
        return self.VIN

    def get_parents(self, parents=None):
        if not parents:
           parents = []
        if self.parent:
           parents.append(self.parent)
           return AssetModel.get_parents(self.parent, parents)
        else:
           return parents

    def is_near_end_of_life(self):
        expiration_date = self.date_in_service + timedelta(days=(self.lifespan_years * 365))
        one_year_from_now = timezone.now().date() + timedelta(days=365)
        return expiration_date <= one_year_from_now and expiration_date > timezone.now().date()