from django.db import models
from .repairs import RepairsModel
from .DetailedUser import DetailedUser

class RepairFile(models.Model):

    # file purposes
    other_support = "other"
    invoice = "invoice"

    file_purpose_choices = [(other_support,"other"), (invoice, "invoice")]

    file_id = models.AutoField(primary_key=True)
    repair = models.ForeignKey(RepairsModel, null=True, on_delete=models.SET_NULL)
    file_type = models.CharField(max_length=150, default='NA')
    file_purpose = models.CharField(choices=file_purpose_choices, max_length=50)
    file_name = models.TextField(max_length=10000, default='NA')
    file_url = models.TextField(max_length=10000, default='NA')
    bytes = models.BigIntegerField(default=0)
    created_by = models.ForeignKey(DetailedUser, on_delete=models.SET_NULL, null=True, default=None, related_name='repair_file_created_by')
    date_created = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.file_id)