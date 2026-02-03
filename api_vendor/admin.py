from django.contrib import admin
from .Models.vendor import VendorModel
from .Models.vendor_departments import VendorDepartments
from .Models.vendor_tasks import VendorTasks
# Register your models here.
admin.site.register(VendorModel)
admin.site.register(VendorDepartments)
admin.site.register(VendorTasks)