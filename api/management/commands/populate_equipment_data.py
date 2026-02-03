from django.core.management.base import BaseCommand, CommandError
from api.Models.asset_model import AssetModel
from api.Models.asset_type import AssetTypeModel
from api.Models.asset_manufacturer import AssetManufacturerModel
from api.Models.equipment_type import EquipmentTypeModel

class Command(BaseCommand):
    help = "Populate asset type, manufacturer and equipment type  tables from Department field in asset model"

    def handle(self, *args, **kwargs):
        asset_types = list(AssetModel.objects.values_list('Asset_Type', flat=True).distinct())
        for t in asset_types:
            new_type, created = AssetTypeModel.objects.get_or_create(name=t)
            if created:
                new_type.save()

        manufacturers = list(AssetModel.objects.values_list('Manufacturer', flat=True).distinct())
        for m in manufacturers:
            new_manufacturer, created = AssetManufacturerModel.objects.get_or_create(name=m)

            if created:
                new_manufacturer.save()

        assets = AssetModel.objects.all()
        for asset in assets:
            asset_type = AssetTypeModel.objects.get(name=asset.Asset_Type)
            manufacturer = AssetManufacturerModel.objects.get(name=asset.Manufacturer)
            
            
            new_etype,created = EquipmentTypeModel.objects.get_or_create(
                model_number=asset.Model_Number,
                fuel=asset.Fuel_Type,
                engine=asset.Engine_Type,
                asset_type=asset_type,
                manufacturer=manufacturer,
                fuel_tank_capacity=asset.fuel_tank_capacity,
                fuel_tank_capacity_unit=asset.fuel_tank_capacity_unit,
                is_rental=asset.is_rental,
                monthly_subscription_cost=asset.monthly_subscription_cost
                )
            if created:
                new_etype.save()
                manufacturer.asset_type.add(asset_type)
            
            
    
