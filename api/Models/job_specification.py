from django.db import models

class JobSpecification(models.Model):

    job_specification_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)