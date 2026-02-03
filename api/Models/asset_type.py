from django.db import models
from .asset_type_checks import AssetTypeChecks
from .DetailedUser import DetailedUser

class AssetTypeModel(models.Model):
    name = models.CharField(max_length=100)
    asset_type_checks = models.ForeignKey(AssetTypeChecks, null=True, on_delete=models.SET_NULL)
    overdue_date_variance = models.IntegerField(default=0, null=False) #measured in days. Number of days the overdue days can be shifted
    due_soon_date_variance = models.IntegerField(default=-7, null=False) #measured in days. Number of days the due soon days can be shifted
    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='asset_type_created_by')
    date_created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='asset_type_modified_by')
    date_modified = models.DateTimeField(auto_now=True)
    custom_fields = models.TextField(null=True)

    def __str__(self):
        return self.name
