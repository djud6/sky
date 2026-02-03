from django.db import models
from .asset_model import AssetModel
from .DetailedUser import DetailedUser

class UserTableLayoutModel(models.Model):
    user=models.ForeignKey(DetailedUser,on_delete=models.CASCADE)
    
    key=models.CharField(max_length=100)
    value=models.TextField(null=True)