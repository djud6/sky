from django.db import models
from .DetailedUser import DetailedUser

class FuelType(models.Model):

    name = models.CharField(max_length=50)

    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='fuel_type_created_by')
    date_created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='fuel_type_modified_by')
    date_updated = models.DateTimeField(auto_now=True)