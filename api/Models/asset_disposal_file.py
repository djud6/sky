from django.db import models
from .asset_disposal import AssetDisposalModel
from .DetailedUser import DetailedUser

class AssetDisposalFile(models.Model):

    # file purposes
    bill_of_sale = "bill of sale"
    insurance = "insurance"
    method_of_payment = "method of payment"
    letter_of_release = "letter of release"
    total_loss_declaration = "total loss declaration"
    tax_receipt = "tax receipt"
    invoice = "invoice"
    proceeds = "proceeds"
    other_support = "other"

    file_purpose_choices = [(bill_of_sale,"bill of sale"), (insurance,"insurance"), (method_of_payment,"method of payment"), 
                            (letter_of_release,"letter of release"), (total_loss_declaration,"total loss declaration"),
                            (tax_receipt,"tax receipt"), (other_support,"other"), (invoice,"invoice"), (proceeds,"proceeds")]

    file_id = models.AutoField(primary_key=True)
    disposal = models.ForeignKey(AssetDisposalModel, null=True, on_delete=models.SET_NULL)
    file_type = models.CharField(max_length=150, default='NA')
    file_purpose = models.CharField(choices=file_purpose_choices, max_length=50)
    file_name = models.TextField(max_length=10000, default='NA')
    file_url = models.TextField(max_length=10000, default='NA')
    bytes = models.BigIntegerField(default=0)
    created_by = models.ForeignKey(DetailedUser, on_delete=models.SET_NULL, null=True, default=None, related_name='disposal_file_created_by')
    date_created = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.file_id)