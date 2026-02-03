from django.db import models
from .DetailedUser import DetailedUser

class NotificationConfiguration(models.Model):

    auto = "auto"
    user = "user"
    location = "location"
    business_unit = "business_unit"
    role = "role"

    recipient_type_choices = [
        (auto, "auto"),
        (user, "user"),
        (location, "location"),
        (business_unit, "business_unit"),
        (role, "role")
    ]

    name = models.CharField(max_length=1000)
    active = models.BooleanField(default=True)

    # notification fields // Holds "-" delimited string of fields that should be included
    fields = models.TextField(null=True, default=None)
    # custom text to appear on notification
    custom_text = models.TextField(null=True, default=None)
    # notification triggers // Holds "-" delimited string of triggers that should be active
    triggers = models.TextField(null=True, default=None)

    # recipients
    recipient_type = models.CharField(choices=recipient_type_choices, max_length=50, default=auto)
    users = models.TextField(null=True, default=None)
    locations = models.TextField(null=True, default=None)
    business_units = models.TextField(null=True, default=None)
    roles = models.TextField(null=True, default=None)

    date_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name="notification_modified_by"
    )

    def __str__(self):
        return str(self.id)