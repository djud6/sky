from django.db import models
from .asset_issue import AssetIssueModel
from .accident_report import AccidentModel
from .repairs import RepairsModel
from .DetailedUser import DetailedUser
from .locations import LocationModel

class AssetIssueModelHistory(models.Model):
    
    critical = "Critical"
    non_critical = "Non-Critical"
    issue_choices = [(critical, "Critical"), (non_critical, "Non-Critical")] 

    accident = "Accident"
    maintenance = "Maintenance"
    operator = "Operator"
    other = "Other"
    issue_result_choices = [(accident, "Accident"), (maintenance, "Maintenance"), (operator, "Operator"), (other, "Other")]

    issue_history_id = models.AutoField(primary_key=True)
    issue = models.ForeignKey(AssetIssueModel, null=True, on_delete=models.SET_NULL)
    custom_id = models.CharField(max_length=100, default="company_name-i-id")

    issue_details = models.TextField(null=True, blank=True)
    issue_title = models.CharField(max_length=150, default="No Title Entered")
    issue_type = models.CharField(choices=issue_choices, default=non_critical, max_length=50)
    accident = models.ForeignKey(AccidentModel, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    repair = models.ForeignKey(RepairsModel, on_delete=models.SET_NULL, blank=True, null=True, default=None)
    issue_result = models.CharField(choices=issue_result_choices, default=other, max_length=100)
    is_resolved = models.BooleanField(default=False)

    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    date = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.SET_NULL, null=True, default=None, related_name='asset_issue_history_modified_by')

    def __str__(self):
        return str(self.issue_history_id)