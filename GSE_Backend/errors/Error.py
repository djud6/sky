class Error:

    error_message_dev = ""
    error_message_user = ""

    def __init__(self, _error_message_dev = "", _error_message_user = ""):
        self.error_message_dev = _error_message_dev
        self.error_message_user = _error_message_user