from django.db import models
from .asset_model import AssetModel
from .DetailedUser import DetailedUser
from .asset_disposal import AssetDisposalModel
from .locations import LocationModel

class AccidentModel(models.Model):


    accident_id = models.AutoField(primary_key=True)
    custom_id = models.CharField(max_length=100, default="company_name-a-id")

    VIN = models.ForeignKey(AssetModel, on_delete=models.PROTECT)
    disposal = models.ForeignKey(AssetDisposalModel, null=True, default=None, on_delete=models.PROTECT)
    
    estimated_return_date = models.DateTimeField(blank=True, null=True)
    accident_report_completed = models.BooleanField() # Internal accident report has been completed.
    is_equipment_failure = models.BooleanField()
    notification_ack = models.BooleanField()
    evaluation_required = models.BooleanField()
    is_resolved = models.BooleanField(default=False) # Has the accident been investigated and resolved.
    is_preventable = models.BooleanField(default=False)
    is_operational = models.BooleanField(default=True)
    date_returned_to_service = models.DateTimeField(null=True, blank=True)
    accident_summary = models.TextField(null=True, blank=True)
    downtime_hours = models.FloatField(default=0)
    
    location = models.ForeignKey(LocationModel, null=True, on_delete=models.SET_NULL)

    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='accident_created_by')
    date_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='accident_modified_by')

    def __str__(self):
        return str(self.VIN)