from django.db import models
from .DetailedUser import DetailedUser

class ErrorReport(models.Model):

    Critical = "critical"
    Undesired = "undesired"
    Feedback = "feedback" 

    issue_type_choices = [(Critical, "critical"), (Undesired, "undesired"), (Feedback, "feedback")]

    #status
    complete = "complete"
    in_progress = "in progress"
    in_queue = "in queue"

    disposal_status_choices = [(complete, "complete"), (in_progress, "in progress"), (in_queue , "in queue")]

    error_report_id = models.AutoField(primary_key=True)
    issue_type = models.CharField(choices=issue_type_choices, max_length=50, default=Feedback)
    error_title = models.CharField(max_length=1000)
    error_description = models.TextField()
    steps_to_reproduce = models.TextField(null=True)
    created_by = models.ForeignKey(DetailedUser, on_delete=models.PROTECT, null=True, default=None, related_name='error_report_created_by')
    date_created = models.DateField(auto_now_add=True)
    status = models.CharField(choices=disposal_status_choices, max_length=50, default=in_queue)