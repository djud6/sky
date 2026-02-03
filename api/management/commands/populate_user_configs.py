from rest_framework import status
from django.core.management.base import BaseCommand
from api.Models.DetailedUser import DetailedUser
from api.Models.user_configuration import UserConfiguration
from core.UserManager.UserUpdater import UserUpdater


class Command(BaseCommand):
    help = "Populate business unit table from Department field in asset model"

    def handle(self, *args, **kwargs):
        
        databases = ["fmt"]

        for db_name in databases:
            print("-----------------------------------------")
            print("Updating database: " + str(db_name))
            print("-----------------------------------------")
            
            users = DetailedUser.objects.using(db_name).all()

            for user in users:
                if not UserConfiguration.objects.using(db_name).filter(user=user).exists():
                    user_config, user_config_response = UserUpdater.create_user_configuration(user)
                    if user_config_response.status_code != status.HTTP_201_CREATED:
                        print("Failed to create config for ser (" + str(user.email) + ")")
                        print("Extra details: ")
                        print(user_config_response.data)
                    print("Created config for user (" + str(user.email) + ")")
                else:
                    print("Configuration already exists for user (" + str(user.email) + ")")

                
