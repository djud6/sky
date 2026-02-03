from django.db import models
from api.Models.Cost.currency import Currency

class SnapshotDailyCurrency(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    currency_value = models.FloatField()
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.currency)