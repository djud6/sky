from django.db import models

class RolePermissions(models.Model):

    operator = "operator"
    supervisor = "supervisor"
    manager = "manager"
    executive = "executive"
    user_roles = [(operator, operator), (manager, manager), (executive, executive), (supervisor, supervisor)]

    role = models.CharField(choices=user_roles, default=operator, max_length=50)
    #Dashboards
    dashboard = models.BooleanField(default=False)
    dashboard_operator = models.BooleanField(default=False)
    #Fleet at a glance permisisons
    fleet_at_a_glance = models.BooleanField(default=False)
    fleet_at_a_glance_executive = models.BooleanField(default=False)
    fleet_at_a_glance_manager = models.BooleanField(default=False)
    fleet_overview = models.BooleanField(default=False)
    #Asset Request Permisisons
    asset_request = models.BooleanField(default=False)
    asset_request_new_order = models.BooleanField(default=False)
    asset_request_list = models.BooleanField(default=False)
    #Repairs permissions
    repairs = models.BooleanField(default=False)
    repairs_list = models.BooleanField(default=False)
    repairs_new_request = models.BooleanField(default=False)
    #Maintenance Permissions
    maintenance = models.BooleanField(default=False)
    maintenance_status = models.BooleanField(default=False)
    maintenance_new_request = models.BooleanField(default=False)
    maintenance_forecast = models.BooleanField(default=False)
    maintenance_lookup = models.BooleanField(default=False)
    #Incidents permissions
    incidents = models.BooleanField(default=False)
    incidents_list = models.BooleanField(default=False)
    incidents_new_report = models.BooleanField(default=False)
    #Issues permissions
    issues = models.BooleanField(default=False)
    issues_new = models.BooleanField(default=False)
    issues_list = models.BooleanField(default=False)
    issues_search = models.BooleanField(default=False)
    #Operators permissions
    operators = models.BooleanField(default=False)
    operators_daily_check = models.BooleanField(default=False)
    operators_search = models.BooleanField(default=False)
    unfinished_checks = models.BooleanField(default=False)
    #Energy permissions
    energy = models.BooleanField(default=False)
    energy_fuel_tracking = models.BooleanField(default=False)
    fuel_orders = models.BooleanField(default=False)
    fuel_transactions = models.BooleanField(default=False)
    #Asset removal permissions
    asset_removal = models.BooleanField(default=False)
    asset_removal_new = models.BooleanField(default=False)
    asset_removal_list = models.BooleanField(default=False)
    #Approval request permissions
    approval_request = models.BooleanField(default=False)
    #Asset Transfers permissions
    asset_transfers = models.BooleanField(default=False)
    asset_transfers_current_transfers = models.BooleanField(default=False)
    asset_transfers_new_transfer_request = models.BooleanField(default=False)
    asset_transfers_map = models.BooleanField(default=False)
    #Asset Log
    asset_log = models.BooleanField(default=False)
