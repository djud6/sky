from django.db import models

class Currency(models.Model):

    code = models.CharField(max_length=50)
    number = models.CharField(max_length=50)
    name = models.CharField(max_length=50)