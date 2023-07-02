class RWSException(Exception):
    """Base class for all RWS application exceptions"""

class RWSTaskTimeLimitImpossible(RWSException):
    """Exception thrown when the time to complete a task is so low that the task cannot be completed"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.timeLimit = kwargs.get('timeLimit')
        self.minTimeToComplete = kwargs.get('minTimeToComplete')

    