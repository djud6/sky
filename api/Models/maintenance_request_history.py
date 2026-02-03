from django.db import models
from .maintenance_request import MaintenanceRequestModel
from .inspection_type import InspectionTypeModel
from .approved_vendors import ApprovedVendorsModel
from .locations import LocationModel
from .DetailedUser import DetailedUser

class MaintenanceRequestModelHistory(models.Model):
    maintenance_history_id = models.AutoField(primary_key=True)
    maintenance = models.ForeignKey(MaintenanceRequestModel, on_delete=models.CASCADE)
    work_order = models.CharField(max_length=100, default="Company_name-m-id")

    inspection_type = models.ForeignKey(InspectionTypeModel, null=True, on_delete=models.SET_NULL)
    assigned_vendor = models.ForeignKey(ApprovedVendorsModel, null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now_add=True)
    location = models.ForeignKey(LocationModel, null=True, on_delete=models.SET_NULL)
    date_completed = models.DateField(blank=True, null=True)
    estimated_delivery_date = models.DateField(blank=True, null=True)
    requested_delivery_date = models.DateField(blank=True, null=True)
    vendor_contacted_date = models.DateField(blank=True, null=True)
    available_pickup_date = models.DateField(blank=True, null=True)
    vendor_email = models.CharField(max_length=100, blank=True, default="NA")
    mileage = models.FloatField(max_length=50, default=-1)
    hours = models.FloatField(max_length=50, default=-1)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='maintenance_history_modified_by')
    status = models.CharField(max_length=100, default="NA")

    def __str__(self):
        return str(self.maintenance_history_id)