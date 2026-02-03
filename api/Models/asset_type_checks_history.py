from django.db import models
from django.db.models.deletion import SET_NULL
from .DetailedUser import DetailedUser
from .asset_type_checks import AssetTypeChecks

class AssetTypeChecksHistory(models.Model):
    
    asset_type_checks = models.ForeignKey(AssetTypeChecks, null=True, on_delete=SET_NULL)

    asset_type_name = models.CharField(max_length=100)

    # ASSET TYPE CHECKS
    # ==================
    tires = models.BooleanField(default=False)
    wheels = models.BooleanField(default=False)
    horn = models.BooleanField(default=False)
    fuel = models.BooleanField(default=False)
    mirrors = models.BooleanField(default=False)
    glass = models.BooleanField(default=False)
    overhead_guard = models.BooleanField(default=False)
    steps = models.BooleanField(default=False)
    forks = models.BooleanField(default=False)
    operator_cab = models.BooleanField(default=False)
    cosmetic_damage = models.BooleanField(default=False)
    brakes = models.BooleanField(default=False)
    steering = models.BooleanField(default=False)
    attachments = models.BooleanField(default=False)
    mud_flaps = models.BooleanField(default=False)
    electrical_connectors = models.BooleanField(default=False)
    air_pressure = models.BooleanField(default=False)
    boom_extensions = models.BooleanField(default=False)
    spreader_functions = models.BooleanField(default=False)

    # Lights
    lights = models.BooleanField(default=False)
    headlights = models.BooleanField(default=False)
    backup_lights = models.BooleanField(default=False)
    trailer_light_cord = models.BooleanField(default=False)

    # Fluids
    fluids = models.BooleanField(default=False)
    oil = models.BooleanField(default=False)
    transmission_fluid = models.BooleanField(default=False)
    steering_fluid = models.BooleanField(default=False)
    hydraulic_fluid = models.BooleanField(default=False)
    brake_fluid = models.BooleanField(default=False)

    # Safety Equipment
    safety_equipment = models.BooleanField(default=False)
    fire_extinguisher = models.BooleanField(default=False)

    # Leaks
    leaks = models.BooleanField(default=False)
    hydraulic_hoses = models.BooleanField(default=False)
    trailer_air_lines = models.BooleanField(default=False)
    other_leaks = models.BooleanField(default=False)

    date = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='asset_type_checks_history_modified_by')
            
    def __str__(self):
        return self.id