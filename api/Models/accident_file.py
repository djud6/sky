from django.db import models
from api.Models.accident_report import AccidentModel

class AccidentFileModel(models.Model):

    file_id = models.AutoField(primary_key=True)
    accident = models.ForeignKey(AccidentModel, null=True, on_delete=models.SET_NULL)
    file_type = models.CharField(max_length=150, default='NA')
    file_name = models.TextField(max_length=10000, default='NA')
    file_url = models.TextField(max_length=10000, default='NA')
    bytes = models.BigIntegerField(default=0)
    file_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.file_id)