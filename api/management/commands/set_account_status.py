from rest_framework.response import Response
from rest_framework import status
from django.core.management.base import BaseCommand, CommandError
from api_auth.Auth_User.User import User
from api.Models.DetailedUser import DetailedUser
from core.UserManager.UserHelper import UserHelper
from core.CompanyManager.CompanyHelper import CompanyHelper
from core.Helper import HelperMethods
import sys


class Command(BaseCommand):
    help = "Sets accounts for a specific schema(s) to active/inactive."

    def add_arguments(self, parser):
        parser.add_argument("--status", type=str)

    def handle(self, *args, **kwargs):
        databases = ["fmt", "fmt_test"]
        exclude = []  # Any accounts to be excluded
        status = HelperMethods.validate_bool(str(kwargs["status"][0]).strip())
        relevant_accounts = User.objects.using("auth_db").filter(db_access__in=databases)

        for account in relevant_accounts:
            try:
                print(
                    "Updating is_active status of "
                    + str(account.username)
                    + " to "
                    + str(status)
                    + ". ("
                    + str(account.db_access)
                    + ")"
                )

                account.is_active = status
                account.save()

                print("Update complete.")
                print("--------------------------")
            except Exception as e:
                print("Update failed. Skipping account.")
                print(e)
