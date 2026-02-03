from django.db import models
from .DetailedUser import DetailedUser

class AssetIssueCategory(models.Model):

    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100)

    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='asset_issue_category_created_by')
    date_created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='asset_issue_category_modified_by')
    date_updated = models.DateTimeField(auto_now=True)