from django.db import models

class SnapshotDailyCounts(models.Model):

    asset_count = models.IntegerField()
    user_count = models.IntegerField()
    
    date_created = models.DateTimeField(auto_now_add=True)
