from django.db import models
from .Company import Company
from .locations import LocationModel
from .RolePermissions import RolePermissions
from .business_unit import BusinessUnitModel
from .cost_centre import CostCentreModel

class DetailedUser(models.Model):

    detailed_user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    location = models.ManyToManyField(LocationModel, related_name='user')
    business_unit = models.ForeignKey(BusinessUnitModel, null=True, on_delete=models.SET_NULL)
    cost_allowance = models.IntegerField()
    company = models.ForeignKey(Company, null=True, on_delete=models.SET_NULL)
    role_permissions = models.ForeignKey(RolePermissions, null=True, on_delete=models.SET_NULL)
    image_url = models.TextField(max_length=10000, default='NA')
    agreement_accepted = models.BooleanField(default=False)
    first_time_login = models.BooleanField(default=True)
    cost_centre = models.ForeignKey(CostCentreModel, null=True, on_delete=models.SET_NULL)
    
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['cost_allowance', 'company']

    def __str__(self):
        return self.email