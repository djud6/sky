from django.db import models

class SnapshotDailyLocationCounts(models.Model):

    active_asset_count = models.IntegerField()
    all_asset_count = models.IntegerField()
    daily_check_count = models.IntegerField()
    location = models.IntegerField()
    date_of_checks = models.DateField()
    date_created = models.DateTimeField(auto_now_add=True)