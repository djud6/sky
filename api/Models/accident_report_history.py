from django.db import models
from .accident_report import AccidentModel
from .DetailedUser import DetailedUser
from .locations import LocationModel

class AccidentModelHistory(models.Model):
    accident_history_id = models.AutoField(primary_key=True)
    accident = models.ForeignKey(AccidentModel, on_delete=models.CASCADE)
    custom_id = models.CharField(max_length=100, default="company_name-a-id")

    estimated_return_date = models.DateTimeField(blank=True, null=True)
    accident_report_completed = models.BooleanField()
    is_equipment_failure = models.BooleanField()
    notification_ack = models.BooleanField()
    evaluation_required = models.BooleanField()
    is_resolved = models.BooleanField(default=False)
    is_preventable = models.BooleanField(default=False)
    is_operational = models.BooleanField(default=True)
    date_returned_to_service = models.DateTimeField(null=True, blank=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='accident_history_modified_by')
    accident_summary = models.TextField(null=True, blank=True)
    downtime_hours = models.FloatField(default=0)

    location = models.ForeignKey(LocationModel, null=True, on_delete=models.SET_NULL)

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.accident_history_id)