from django.db import models
from .approved_vendor_departments import ApprovedVendorDepartments
from .approved_vendor_tasks import ApprovedVendorTasks

class ApprovedVendorRequest(models.Model):
    vendor_department = models.ForeignKey(ApprovedVendorDepartments, on_delete=models.SET_NULL, null=True)
    vendor_task = models.ForeignKey(ApprovedVendorTasks, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        string = self.vendor_department +"/"+ self.vendor_task
        return string
