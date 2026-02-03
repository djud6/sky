from django.db import models
from .asset_model import AssetModel
from .accident_report import AccidentModel
from .repairs import RepairsModel
from .DetailedUser import DetailedUser
from .asset_issue_category import AssetIssueCategory
from .locations import LocationModel

class AssetIssueModel(models.Model):
    
    critical = "Critical"
    non_critical = "Non-Critical"
    issue_choices = [(critical, "Critical"), (non_critical, "Non-Critical")] 

    accident = "Accident"
    maintenance = "Maintenance"
    operator = "Operator"
    other = "Other"
    issue_result_choices = [(accident, "Accident"), (maintenance, "Maintenance"), (operator, "Operator"), (other, "Other")]

    issue_id = models.AutoField(primary_key=True)
    custom_id = models.CharField(max_length=100, default="company_name-i-id")

    VIN = models.ForeignKey(AssetModel, on_delete=models.PROTECT)
    category = models.ForeignKey(AssetIssueCategory, null=True, on_delete=models.SET_NULL)
    issue_details = models.TextField(null=True, blank=True)
    issue_title = models.CharField(max_length=150, default="No Title Entered")
    
    issue_type = models.CharField(choices=issue_choices, default=non_critical, max_length=50)
    accident_id = models.ForeignKey(AccidentModel, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    repair_id = models.ForeignKey(RepairsModel, on_delete=models.SET_NULL, blank=True, null=True, default=None)
    issue_result = models.CharField(choices=issue_result_choices, default=other, max_length=100)
    is_resolved = models.BooleanField(default=False)

    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    created_by = models.ForeignKey(DetailedUser, on_delete=models.SET_NULL, null=True, default=None, related_name='asset_issue_created_by')
    issue_created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.SET_NULL, null=True, default=None, related_name='asset_issue_modified_by')
    issue_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.VIN)
