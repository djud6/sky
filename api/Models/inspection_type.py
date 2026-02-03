from django.db import models

class InspectionTypeModel(models.Model):
    A_CHECK = "A"
    B_CHECK = "B"
    C_CHECK = "C"
    MOT_CHECK = "MOT"
    O_CHECK = "O"
    P_CHECK = "P"
    S_CHECK = "S"
    PI_CHECK = "PI"
    SB_CHECK = "SB"
    MOD_CHECK = "MOD"
    inspection_names = [(A_CHECK, "Minor Inspection"), (B_CHECK, "Major Inspection"), (C_CHECK, "Bi-Weekly Inspection"), (MOT_CHECK, "Ministry Of Transport"), (O_CHECK, "Operational Inspection"),
     (P_CHECK, "Pre-Seasonal Inspection"), (S_CHECK, "Safety Inspection"), (PI_CHECK, "Provincial Inspection"), (SB_CHECK, "Service Bulletin"), (MOD_CHECK, "Modification")]
    inspection_codes = [(A_CHECK, A_CHECK), (B_CHECK, B_CHECK), (C_CHECK, C_CHECK), (MOT_CHECK, MOT_CHECK), (O_CHECK, O_CHECK),
     (P_CHECK, P_CHECK), (S_CHECK, S_CHECK), (PI_CHECK, PI_CHECK), (SB_CHECK, SB_CHECK), (MOD_CHECK, MOD_CHECK)]

    inspection_name = models.CharField(choices=inspection_names, max_length=50)
    inspection_code = models.CharField(choices=inspection_codes, max_length=50)
    required_at = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.inspection_name