from django.core.management import call_command
import sys
from django.core.management.base import BaseCommand, CommandError
from django.test import client
from django.conf import settings

class Command(BaseCommand):
    help = "Making database migrations for all databases"

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str)

    def handle(self, *args, **kwargs):
        print("Configured databases:")
        print(list(settings.DATABASES.keys()))
        print("------------------------------------------------------")
        client_db_names = self.gen_client_db_names(num_of_clients=10)
        databases = ["dev", "dev_staging", "westjet", "gbcs", "district_of_houston", "traxx", "schlumberger", "fmt", "mobile_app", "taqa"] + client_db_names
        auth = "auth_db"
        auth_app_name = "api_auth"

        # [0] = Which app
        app_name = kwargs['app_name']

        # migrate
        if(app_name != auth_app_name):
            for db in databases:
                print("Migrating to database: " + str(db))
                call_command("migrate", app_name, "--database=" + db)
                print("------------------------------------------------------")
        else:
            call_command("migrate", auth_app_name, "--database=" + auth)
            
        #self.stdout.write(self.style.SUCCESS(kwargs['app_name']))

    def gen_client_db_names(self, num_of_clients=0):
        client_db_names = []
        count = 1
        while count <= num_of_clients:
            client_db_names.append('client_' + str(count))
            count += 1
        return client_db_names

