from django.db import models

class FleetGuru(models.Model):
    process = models.CharField(max_length=50) # Process that the fleet guru is talking about
    title = models.CharField(max_length=150)
    description = models.TextField()
    image_url = models.CharField(max_length=150, null=True, blank=True)
