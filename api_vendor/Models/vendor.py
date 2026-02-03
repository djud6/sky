from django.db import models
from .vendor_departments import VendorDepartments
from .vendor_tasks import VendorTasks
class VendorModel(models.Model):
    vendor_id = models.AutoField(primary_key=True)
    vendor_name = models.CharField(max_length=100)
    vendor_department = models.ForeignKey(VendorDepartments, on_delete=models.CASCADE)
    vendor_task = models.ForeignKey(VendorTasks, on_delete=models.CASCADE, null=True)
    vendor_green_rating = models.FloatField(default=0)
    address = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=150)
    website = models.CharField(max_length=150, blank=True)
    primary_email = models.EmailField()
    is_vendor_green = models.BooleanField()

    def __str__(self):
        return self.vendor_name