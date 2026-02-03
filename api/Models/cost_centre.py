from django.db import models

class CostCentreModel(models.Model):
    cost_centre_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name