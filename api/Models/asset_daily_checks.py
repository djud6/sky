from django.db import models
from .asset_model import AssetModel
from .DetailedUser import DetailedUser
from .locations import LocationModel


class AssetDailyChecksModel(models.Model):
    daily_check_id = models.AutoField(primary_key=True)
    custom_id = models.CharField(max_length=100, default="company_name-dc-id")

    VIN = models.ForeignKey(AssetModel, on_delete=models.PROTECT)
    operable = models.BooleanField()
    mileage = models.FloatField(max_length=50, null=True, default=-1)
    hours = models.FloatField(max_length=50, null=True, default=-1)
    is_tagout = models.BooleanField(default=False)

    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='asset_daily_check_created_by')
    date_created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='asset_daily_check_modified_by')
    date_modified = models.DateTimeField(auto_now=True)

    # ASSET TYPE CHECKS
    # ==================
    tires = models.BooleanField(null=True)
    wheels = models.BooleanField(null=True)
    horn = models.BooleanField(null=True)
    fuel = models.IntegerField(null=True)  # Will hold the percentage of fuel in asset
    mirrors = models.BooleanField(null=True)
    glass = models.BooleanField(null=True)
    overhead_guard = models.BooleanField(null=True)
    steps = models.BooleanField(null=True)
    forks = models.BooleanField(null=True)
    operator_cab = models.BooleanField(null=True)
    cosmetic_damage = models.BooleanField(null=True)
    brakes = models.BooleanField(null=True)
    steering = models.BooleanField(null=True)
    attachments = models.BooleanField(null=True)
    mud_flaps = models.BooleanField(null=True)
    electrical_connectors = models.BooleanField(null=True)
    air_pressure = models.BooleanField(null=True)
    boom_extensions = models.BooleanField(null=True)
    spreader_functions = models.BooleanField(null=True)

    # Lights
    headlights = models.BooleanField(null=True)
    backup_lights = models.BooleanField(null=True)
    trailer_light_cord = models.BooleanField(null=True)

    # Fluids
    oil = models.BooleanField(null=True)
    transmission_fluid = models.BooleanField(null=True)
    steering_fluid = models.BooleanField(null=True)
    hydraulic_fluid = models.BooleanField(null=True)
    brake_fluid = models.BooleanField(null=True)

    # Leaks
    hydraulic_hoses = models.BooleanField(null=True)
    trailer_air_lines = models.BooleanField(null=True)
    other_leaks = models.BooleanField(null=True)

    # Safety Equipment
    lifesaving_equipments = models.BooleanField(null=True)
    engine_and_all_mechanical = models.BooleanField(null=True)
    communication = models.BooleanField(null=True)
    steering_and_hydraulics = models.BooleanField(null=True)
    fire_extinguisher = models.BooleanField(null=True)
    electrical = models.BooleanField(null=True)
    navigation_and_strobe_lights = models.BooleanField(null=True)
    fuel_systems = models.BooleanField(null=True)
    anchoring_system = models.BooleanField(null=True)

    def __str__(self):
        return str(self.VIN)
