from django.db import models

class LocationModel(models.Model):
    location_id = models.AutoField(primary_key=True)
    location_code = models.CharField(max_length=10)
    location_name = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True)
    longitude = models.FloatField(blank=True)

    def __str__(self):
        return self.location_code