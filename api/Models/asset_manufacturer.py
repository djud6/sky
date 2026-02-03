from django.db import models
from .asset_type import AssetTypeModel
from .DetailedUser import DetailedUser

class AssetManufacturerModel(models.Model):
    name = models.CharField(max_length=100)
    asset_type = models.ManyToManyField(AssetTypeModel, related_name='manufacturers')
    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='manufacturer_created_by')
    date_created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='manufacturer_type_modified_by')
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name