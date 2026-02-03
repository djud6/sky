from django.db import models
from .repairs import RepairsModel
from .approved_vendors import ApprovedVendorsModel
from .locations import LocationModel
from .DetailedUser import DetailedUser

class RepairsModelHistory(models.Model):
    repair_history_id = models.AutoField(primary_key=True)
    repair = models.ForeignKey(RepairsModel, on_delete=models.CASCADE)
    work_order = models.CharField(max_length=100, default="Company_name-r-id")

    vendor = models.ForeignKey(ApprovedVendorsModel, null=True, on_delete=models.SET_NULL)
    location = models.ForeignKey(LocationModel, null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    requested_delivery_date = models.DateTimeField(blank=True, null=True)
    estimated_delivery_date = models.DateTimeField(blank=True, null=True)
    available_pickup_date = models.DateTimeField(blank=True, null=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    down_time = models.IntegerField(blank=True, null=True)
    vendor_contacted_date = models.DateTimeField(blank=True, null=True)
    vendor_email = models.CharField(max_length=100, blank=True, default="NA")
    mileage = models.FloatField(max_length=50, default=-1)
    hours = models.FloatField(max_length=50, default=-1)
    modified_by = models.ForeignKey(DetailedUser, on_delete=models.SET_NULL, null=True, default=None, related_name='repair_history_modified_by')
    status = models.CharField(max_length=100, default="NA")
    
    def __str__(self):
        return str(self.repair_history_id)