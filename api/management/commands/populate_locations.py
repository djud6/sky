from django.core.management.base import BaseCommand, CommandError
from api.Models.asset_model import AssetModel
from api.Models.locations import LocationModel

class Command(BaseCommand):
    help = "Populate business unit table from Department field in asset model"

    def handle(self, *args, **kwargs):
        locations = list(AssetModel.objects.values_list('Location_IATA', flat=True).distinct())
        for loc in locations:
            new_location = LocationModel(location_code=loc, location_name=loc, latitude=0, longitude=0)
            new_location.save()
            
    
