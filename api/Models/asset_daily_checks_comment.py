from django.db import models
from .asset_daily_checks import AssetDailyChecksModel

class AssetDailyChecksComment(models.Model):
    daily_check_comment_id = models.AutoField(primary_key=True)
    daily_check = models.ForeignKey(AssetDailyChecksModel, null=True, on_delete=models.SET_NULL)
    comment = models.TextField()
    check = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)