from django.db import models
from django.core.validators import MaxValueValidator
from django.db.models.fields import CharField
from .DetailedUser import DetailedUser

class UserConfiguration(models.Model):

    user = models.ForeignKey(DetailedUser, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now=True)

    # Sound configurations
    sound = models.BooleanField(default=True)
    sound_percentage = models.PositiveIntegerField(validators=[MaxValueValidator(100)], default=20)

    # Dashboard configuration // Holds JSON of KPI layout on dashboard
    dashboard_layout = models.TextField(null=True)

    #table filter configuration
    table_filter = models.TextField(null=True)

    def __str__(self):
        return str(self.user)
