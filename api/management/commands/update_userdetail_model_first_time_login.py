from django.core.management.base import BaseCommand

from api.Models.DetailedUser import DetailedUser


class Command(BaseCommand):
    help = "Update first_time_login to False for all users who have previously registered"

    def handle(self, *args, **kwargs):

        databases = ["dev", "dev_staging", "westjet", "gbcs", "district_of_houston", "traxx", "schlumberger", "fmt", "mobile_app"]

        for db_name in databases:
            print("-----------------------------------------")
            print("Updating database: " + str(db_name))
            print("-----------------------------------------")
            Command.update_first_time_login(db_name)

    @staticmethod
    def update_first_time_login(db_name):
        detail_user_objects_list = DetailedUser.objects.using(db_name).all()

        for detail_user in detail_user_objects_list:
            try:
                print("Setting detaileduser username: " + str(detail_user.email) + " ID: " + str(detail_user.detailed_user_id) +
                      " first_time_login to False")

                detail_user.first_time_login = False
                detail_user.save()
            except Exception as e:
                print(e)
                continue