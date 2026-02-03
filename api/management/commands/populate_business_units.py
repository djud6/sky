from django.core.management.base import BaseCommand, CommandError
from api.Models.asset_model import AssetModel
from api.Models.business_unit import BusinessUnitModel

class Command(BaseCommand):
    help = "Populate business unit table from Department field in asset model"

    def handle(self, *args, **kwargs):
        units = list(AssetModel.objects.values_list('department', flat=True).distinct())
        for unit in units:
            new_unit = BusinessUnitModel(name=unit)
            new_unit.save()
    
