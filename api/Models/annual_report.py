from django.db import models
from .asset_model import AssetModel
from .asset_file import AssetFile

class AnnualReport(models.Model):
    
    VIN=models.ForeignKey(AssetModel,on_delete=models.PROTECT)
    file=models.ForeignKey(AssetFile,on_delete=models.PROTECT)
    
    lifesaving_ok=models.BooleanField()
    lifesaving_notes=models.TextField(blank=True)
    engine_ok=models.BooleanField()
    engine_notes=models.TextField(blank=True)
    communications_ok=models.BooleanField()
    communications_notes=models.TextField(blank=True)
    bilge_pump_ok=models.BooleanField()
    bilge_pump_notes=models.TextField(blank=True)
    steering_controls_ok=models.BooleanField()
    steering_controls_notes=models.TextField(blank=True)
    hatches_ok=models.BooleanField()
    hatches_notes=models.TextField(blank=True)
    emergency_drills_ok=models.BooleanField()
    emergency_drills_notes=models.TextField(blank=True)
    fire_extinguishers_ok=models.BooleanField()
    fire_extinguishers_notes=models.TextField(blank=True)
    hull_ok=models.BooleanField()
    hull_notes=models.TextField(blank=True)
    electrical_ok=models.BooleanField()
    electrical_notes=models.TextField(blank=True)
    lights_ok=models.BooleanField()
    lights_notes=models.TextField(blank=True)
    fuel_systems_ok=models.BooleanField()
    fuel_systems_notes=models.TextField(blank=True)
    anchoring_ok=models.BooleanField()
    anchoring_notes=models.TextField(blank=True)
    guard_rails_lines_ok=models.BooleanField()
    guard_rails_lines_notes=models.TextField(blank=True)
    crew_qualifications_ok=models.BooleanField()
    crew_qualifications_notes=models.TextField(blank=True)

    signature_name=models.CharField(max_length=100,null=True)
    signature_date=models.CharField(max_length=100,null=True)