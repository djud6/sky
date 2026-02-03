from django.core.management.base import BaseCommand
from api.Models.accident_report import AccidentModel
from api.Models.asset_model import AssetModel
from random import choice, randint
from datetime import date, timedelta
class Command(BaseCommand):
    def handle(self, *args, **options):
        # delete current accidents
        AccidentModel.objects.all().delete()
        available_vins = list(AssetModel.objects.values_list('VIN', flat=True))
        for i in range(0,50):
            # select a random asset
            vin = choice(available_vins)

            # select a random date in the past year

            random_date = date.today() - timedelta(days=randint(1,365)) 
            
            # create an accident model

            new_accident=AccidentModel.objects.create(VIN_id=vin, date_created=random_date, date_modified=random_date, accident_report_completed=True, is_equipment_failure=False, notification_ack=False, evaluation_required=False)
            
            new_accident.save()
            new_accident.date_created = random_date
            new_accident.save()
