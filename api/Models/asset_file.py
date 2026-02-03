from django.db import models
from .asset_model import AssetModel
from .DetailedUser import DetailedUser

class AssetFile(models.Model):

    asset_image = "asset-image"
    warranty = "warranty"
    insurance = "insurance"
    registration = "registration"
    invoice = "invoice"
    vin_support = "vin"
    usage_support = "usage"
    annual_report = "annual_report"
    other_support = "other"
    other = "other"

    file_purpose_choices = [(asset_image, "asset-image"), 
                            (warranty, "warranty"), 
                            (insurance, "insurance"), 
                            (registration, "registration"),
                            (vin_support, "vin"), 
                            (usage_support, "usage"), 
                            (invoice, "invoice"), 
                            (annual_report, "annual_report"),
                            (other_support, "other"), 
                            (other, "other")]  # Add the additional 'other' choice

    file_id = models.AutoField(primary_key=True)
    VIN = models.ForeignKey(AssetModel, on_delete=models.PROTECT)
    file_type = models.CharField(max_length=150, default='NA')
    file_purpose = models.CharField(choices=file_purpose_choices, max_length=50)
    file_name = models.TextField(max_length=10000, default='NA')
    file_url = models.TextField(max_length=10000, default='NA')
    bytes = models.BigIntegerField(default=0)
    created_by = models.ForeignKey(DetailedUser, on_delete=models.SET_NULL, null=True, default=None, related_name='asset_file_created_by')
    date_created = models.DateField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.SET_NULL, null=True, default=None, related_name='asset_file_modified_by')
    date_modified = models.DateField(auto_now=True)
    expiration_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.file_id)
