from django.db import models

from api.Models.DetailedUser import DetailedUser
from .asset_transfer import AssetTransfer

class TransferFile(models.Model):
    # file purposes
    other = "other"
    approval = "approval"
    cancellation = "cancellation"
    transit_document = "transit_document"

    file_purpose_choices = [(other, "other"), (approval, "approval"), (cancellation, "cancellation"), (transit_document, "transit_document")]

    file_id = models.AutoField(primary_key=True)
    transfer = models.ForeignKey(AssetTransfer, null=True, on_delete=models.SET_NULL)
    file_type = models.CharField(max_length=150, default='NA')
    file_name = models.TextField(max_length=10000, default='NA')
    file_url = models.TextField(max_length=10000, default='NA')
    bytes = models.BigIntegerField(default=0)
    file_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(DetailedUser, on_delete=models.SET_NULL, null=True, default=None, related_name='transfer_file_created_by')
    file_purpose = models.CharField(choices=file_purpose_choices, default='other', max_length=50)

    def __str__(self):
        return str(self.file_id)