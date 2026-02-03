from django.db import models
from .asset_model import AssetModel
from .DetailedUser import DetailedUser
from .locations import LocationModel

class AssetLog(models.Model):

    comment = "comment"
    event = "event"
    log_type_choices = [(comment, "comment"), (event, "event")]

    operator_check = "operator check"
    accident = "accident"
    issue = "issue"
    repair = "repair"
    maintenance = "maintenance"
    maintenance_rule = "maintenance rule"
    disposal = "disposal"
    transfer = "transfer"
    event_type_choices = [(operator_check, "operator check"), (accident, "accident"), (issue, "issue"), (repair, "repair"), (maintenance, "maintenance"), (maintenance_rule, "maintenance rule"), (disposal, "disposal"), (transfer, "transfer")]

    asset_log_id = models.AutoField(primary_key=True)
    VIN = models.ForeignKey(AssetModel, on_delete=models.PROTECT)
    log_type = models.CharField(choices=log_type_choices, max_length=50, default=event)
    event_type = models.CharField(choices=event_type_choices, max_length=50, null=True)
    event_id = models.CharField(max_length=100, null=True)
    content = models.TextField()

    location = models.ForeignKey(LocationModel, on_delete=models.SET_NULL, null=True)   

    created_by = models.ForeignKey(DetailedUser, on_delete=models.SET_NULL, null=True, default=None, related_name='asset_log_created_by')   
    asset_log_created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.SET_NULL, null=True, default=None, related_name='asset_log_modified_by')
    asset_log_updated = models.DateTimeField(auto_now=True)
