from django.db import models


class Company(models.Model):

    unknown = "NA"
    client = "client"
    vendor = "vendor"
    company_type_choices = [
        (unknown, "NA"),
        (client, "client"),
        (vendor, "vendor"),
    ]

    active = models.BooleanField(default=False)
    needs_reset = models.BooleanField(default=False)
    is_uat = models.BooleanField(default=False)
    upload_complete = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, unique=True)
    company_db_access = models.CharField(max_length=255)

    company_type = models.CharField(
        choices=company_type_choices, max_length=255, default=unknown
    )


def __str__(self):
    return self.company_name