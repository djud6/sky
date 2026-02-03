from rest_framework.response import Response
from rest_framework import status
from django.core.management.base import BaseCommand, CommandError
from api_auth.Auth_User.User import User
from api.Models.DetailedUser import DetailedUser
from core.UserManager.UserHelper import UserHelper
from core.CompanyManager.CompanyHelper import CompanyHelper
import sys

# How to use: python .\manage.py create_admin_account --password "some password" --db_access "fmt" --company "FMT"

class Command(BaseCommand):
    help = "Meant to create the first superuser in a fresh db"

    def add_arguments(self, parser):
        parser.add_argument('--password', action='append', type=str)
        parser.add_argument('--db_access', action='append', type=str)
        parser.add_argument('--company', action='append', type=str)


    def handle(self, *args, **kwargs):
        email = "gbcs-admin2@skyit.services"
        password = str(kwargs['password'][0]).strip()
        db_access = str(kwargs['db_access'][0]).strip()
        first_name = "GBCS"
        last_name = "Admin"
        company, company_response = CompanyHelper.get_company_by_name(str(kwargs['company'][0]), db_access)
        if company_response.status_code != status.HTTP_302_FOUND:
            print("THE SELECTED COMPANY WAS NOT FOUND --> Check db for company name.")
            sys.exit()

        print("Starting creation of superuser -------------")
        print("Setting email to: " + str(email))
        print("Setting password to: " + str(password))
        print("Setting db_access to: " + str(db_access))
        print("Setting first name to: " + str(first_name))
        print("Setting last name to: " + str(last_name))
        print("Setting company to: " + str(company.company_name))

        # Create user
        user_obj = User.objects.create_superuser(email, password, db_access,
        first_name=first_name, 
        last_name=last_name)

        print("Creating detailed user entry...")

        # Create detailed user
        detailed_user_entry = DetailedUser(
            email = email,
            role_permissions = UserHelper.get_role_permissions_obj(3, db_access),
            company = company,
            cost_allowance = 0,
        )

        detailed_user_entry.save()

        print("Done")