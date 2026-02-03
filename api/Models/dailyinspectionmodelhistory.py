from django.db import models

class DailyInspectionHistory(models.Model):

    VIN = models.CharField(max_length=17)
    inspection_date = models.DateField()

    # Lifesaving Equipment
    pfd_lifejacket_ledger = models.TextField(blank=True, null=True) # Should it not be Boolean as well
    throw_bags = models.BooleanField(default=False)
    heaving_line = models.BooleanField(default=False)
    liferings = models.BooleanField(default=False)
    reboarding_device = models.BooleanField(default=False)
    watertight_flashlight = models.BooleanField(default=False)
    pyrotechnic_flares = models.BooleanField(default=False)
    first_aid_kit = models.BooleanField(default=False)

    # Engine and all Mechanical
    engine_working = models.BooleanField(default=False)

    # Communications
    marine_vhf_radio = models.BooleanField(default=False)
    police_radio = models.BooleanField(default=False)
    epirb_registered = models.BooleanField(default=False)

    # Bilge Pump and Bilge Alarms
    bilge_pump_clear = models.BooleanField(default=False)

    # Steering Controls and/or Hydraulics
    steering_controls_operable = models.BooleanField(default=False)

    # All Hatches, Vents and Openings Operable
    hatches_operable = models.BooleanField(default=False)

    # Emergency Drills
    training_skills_exercised = models.BooleanField(default=False)
    drills_entered_logbook = models.BooleanField(default=False)
    emergency_briefings_conducted = models.BooleanField(default=False)

    # Fire Extinguishers and Suppression Systems
    fire_extinguishers_inspected = models.BooleanField(default=False)

    # Hull and Structure
    regular_inspections_completed = models.BooleanField(default=False)

    # Electrical
    electrical_inspections_completed = models.BooleanField(default=False)

    # Navigation and Strobe Lights
    broken_cracked_lenses = models.BooleanField(default=False) # this is just a suggestion but shoudl we keep True for positive
    lights_functioning = models.BooleanField(default=False)

    # Fuel Systems
    fuel_connections_good = models.BooleanField(default=False)
    fuel_containers_stored_properly = models.BooleanField(default=False)

    # Anchoring System
    ground_tackle_inspected = models.BooleanField(default=False)
    bitter_end_attached = models.BooleanField(default=False) 
    #MISSING: ADDED THIS ONE
    anchor_secured = models.BooleanField(default=False) 

    # Guard, Grab Rails and/or Grab Lines
    welds_bolts_screws_good = models.BooleanField(default=False) # Should we not seperate them
    grab_lines_good = models.BooleanField(default=False)

    # Crew Qualifications
    operators_trained = models.BooleanField(default=False)
    crew_equipment_trained = models.BooleanField(default=False)

    # Additional Fields
    vessel_damaged_since_last_report = models.BooleanField(default=False)
    structural_changes_made_since_last_report = models.BooleanField(default=False)


    # def __str__(self):
    #     return str(self)