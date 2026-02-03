from django.db import models
from .Company import Company
from .DetailedUser import DetailedUser
from .locations import LocationModel
from .business_unit import BusinessUnitModel
from .RolePermissions import RolePermissions

class DetailedUserModelHistory(models.Model):

    detailed_user_history_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(DetailedUser, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(unique=False)
    business_unit = models.ForeignKey(BusinessUnitModel, null=True, on_delete=models.SET_NULL)
    cost_allowance = models.IntegerField()
    role_permissions = models.ForeignKey(RolePermissions, null=True, on_delete=models.SET_NULL)
    company = models.ForeignKey(Company, null=True, on_delete=models.SET_NULL)
    image_url = models.TextField(max_length=10000, default='NA')

    def __str__(self):
        return self.email