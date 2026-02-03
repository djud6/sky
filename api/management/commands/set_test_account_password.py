from django.core.management.base import BaseCommand, CommandError
from api_auth.Auth_User.User import User

class Command(BaseCommand):
    help = "Setting test user passwords"

    def add_arguments(self, parser):
        parser.add_argument('password', type=str)

    def handle(self, *args, **kwargs):
        
        dev_databases = ["dev", "dev_staging", "fmt_test", "district_of_houston", "traxx"]
        excluded_accounts = []

        dev_users = User.objects.filter(db_access__in=dev_databases)

        for user in dev_users:
            if not user.email in excluded_accounts:
                try:
                    user.set_password(kwargs['password'])
                    user.save()
                    print("Changed account password for: " + str(user.email))
                except Exception as e:
                    print(e)
                    print("WAS NOT ABLE TO SET ACCOUNT PASSWORD FOR: " + str(user.email))