from django.db import models
from ..Models.locations import LocationModel

class BusinessUnitModel(models.Model):
    business_unit_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100) 
    location = models.ForeignKey(LocationModel, on_delete=models.PROTECT)
    accounting_email = models.EmailField()
    
    def __str__(self):
        return self.name