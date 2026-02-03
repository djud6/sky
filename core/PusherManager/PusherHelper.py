from django.conf import settings
import datetime
import random

class PusherHelper:

    # events for service bus message
    ASBMessageReceived = 'asb_message_received'
    # events for operator's check 
    OpCheckDoneEvent = 'opcheck_done'
    
    # events for approval requests
    ApprovalCreatedEvent = 'approval_created'
    ApprovalApprovedEvent = 'approval_approved'
    ApprovalDeniedEvent = 'approval_denied'
    
    # events for repair 
    RepairCancelledEvent = 'repair_cancelled'
    RepairCreatedEvent = 'repair_created'
    RepairIncompleteEvent = 'repair_incomplete'
    RepairCompleteEvent = 'repair_complete'

    # events for issues
    IssueCreatedEvent = 'issue_created'
    IssueUnresolvedEvent = 'issue_unresolved'
    IssueResolvedEvent = 'issue_resolved'

    # events for maintenance
    MaintenanceCreatedEvent = 'maintenance_created'
    MaintenanceIncompleteEvent = 'maintenance_incomplete'
    MaintenanceCompleteEvent = 'maintenance_complete'
    MaintenanceCancelledEvent = 'maintenance_cancelled'

    # events for accidents
    AccidentCreatedEvent = 'accident_created'
    AccidentResolvedEvent = 'accident_resolved'

    def __init__(self, channel, event, payload, skip_push, history_func):
        self.channel = str(channel).replace(" ", "-")
        self.event = event
        self.payload = payload
        self.skip_push = skip_push
        self.history_func = history_func

    @staticmethod
    def authenticate(channel, socket_id):
        return settings.PUSHER_CLIENT.authenticate(channel=channel, socket_id=socket_id)

    # arguments that the history func expects must be passed in *args
    def push(self, *args):
        res = self.history_func(*args)
        # send pusher event only if it is not skipped and history_func is successful
        if not self.skip_push and res:
            channel_name = f'private-encrypted-{self.channel}'
            settings.PUSHER_CLIENT.trigger(channel_name, self.event, self.payload)
        return res
    
    def push_chunked(self, *args):
        res = self.history_func(*args)
        # send pusher event only if it is not skipped and history_func is successful
        if not self.skip_push and res:
            channel_name = f'private-encrypted-{self.channel}'
            chunk_size = 6000
            random.seed(datetime.datetime.today())
            msg_id = "{}".format(random.random())
            i = 0
            while i*chunk_size < len(self.payload):
                settings.PUSHER_CLIENT.trigger(channel_name, self.event, {
                    'id': msg_id,
                    'index': i,
                    'chunk': self.payload[i*chunk_size : (i+1)*chunk_size],
                    'final': chunk_size*(i+1) >= len(self.payload)
                })
                i = i + 1
        return res
