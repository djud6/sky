from django.db import models
from .approved_vendor_departments import ApprovedVendorDepartments
from .approved_vendor_tasks import ApprovedVendorTasks

class ApprovedVendorsModel(models.Model):
    vendor_id = models.AutoField(primary_key=True)
    vendor_name = models.CharField(max_length=100)
    vendor_department = models.ForeignKey(ApprovedVendorDepartments, on_delete=models.SET_NULL, null=True)
    vendor_task = models.ForeignKey(ApprovedVendorTasks, on_delete=models.SET_NULL, null=True)
    is_vendor_green = models.BooleanField()
    phone_number = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    website = models.CharField(max_length=1000)
    primary_email = models.EmailField()

    def __str__(self):
        return self.vendor_name
