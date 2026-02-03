from django.db import models
from api.Models.Cost.currency import Currency
import uuid

class Company(models.Model):

    unknown = "unknown"
    aukai = "aukai"
    orion = "orion"
    lokomotive = "lokomotive"

    software_choices = [(unknown, "unknown"), (aukai, "aukai"), (orion, "orion"), (lokomotive, "lokomotive")] 

    company_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    company_name = models.CharField(max_length=150)
    company_address = models.CharField(max_length=150, default="Address Not Entered")
    company_phone = models.CharField(max_length=50, default="Phone Not Entered")
    standard_currency = models.ForeignKey(Currency, default=None, on_delete=models.SET_NULL, null=True)
    accounting_email = models.EmailField(unique=True)
    software_logo = models.CharField(max_length=1000, default="NA")
    software_name = models.CharField(choices=software_choices, max_length=50, default=unknown)

    def __str__(self):
        return self.company_name