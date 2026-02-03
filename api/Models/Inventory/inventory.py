from django.db import models
from django.core.exceptions import ValidationError
from ..equipment_type import EquipmentTypeModel
from ..DetailedUser import DetailedUser
from ..locations import LocationModel


class Inventory(models.Model):
    serial = models.CharField(unique=True, max_length=255, null=True)
    custom_id = models.CharField(unique=True, max_length=255, null=True)
    inventory_type = models.CharField(max_length=255)
    description = models.TextField(null=True)
    per_unit_cost = models.FloatField(null=True)
    date_of_manufacture = models.DateField(null=True)
    location = models.ForeignKey(LocationModel, null=True, on_delete=models.SET_NULL)

    # If applicable to the inventory entry (applies to vehicles and other machinery)
    equipment_type = models.ForeignKey(EquipmentTypeModel, null=True, on_delete=models.SET_NULL)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        DetailedUser,
        on_delete=models.PROTECT,
        null=True,
        default=None,
        related_name="inventory_created_by",
    )
    modified_by = models.ForeignKey(
        DetailedUser,
        on_delete=models.PROTECT,
        null=True,
        default=None,
        related_name="inventory_modified_by",
    )

    def clean(self):
        super().clean()
        if self.serial is None and self.custom_id is None:
            raise ValidationError("serial and custom_id are both None")

    def save(self, *args, **kwargs):
        self.clean()
        self.inventory_type = self.inventory_type.lower().replace(" ", "")
        return super(Inventory, self).save(*args, **kwargs)
