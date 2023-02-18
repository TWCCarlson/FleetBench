class taskManager:
    def __init__(self, parent):
        self.parent = parent
        print("Task Manager Class gen")
        # Generates tasks
        # A task contains
        # Pickup loc, dropoff loc, optimal time to complete, maximum time before failure, status
        # Leave room for misc details (weight, etc)
        # Each task should be an instance of a task class

        self.taskList = {}
        self.taskPositionList = {}
        
    def createNewTask(self, **kwargs):
        # The length of a dict is always 1 higher than the numeric id
        self.dictLength = len(self.taskList)
        try:
            ID = kwargs.pop("ID")
        except KeyError:
            ID = self.dictLength
        self.latestTask = taskClass(self, **kwargs, ID=ID, numID = self.dictLength)
        self.taskList[self.dictLength] = self.latestTask
        print(self.taskList)

class taskClass:
    def __init__(self, parent, **kwargs):
        self.parent = parent
        print("Create Task")
        self.numID = kwargs.pop("numID")
        self.name = kwargs.pop("taskName")
        self.pickupPosition = kwargs.pop("pickupPosition")
        self.dropoffPosition = kwargs.pop("dropoffPosition")
        self.timeLimit = kwargs.pop("timeLimit")
        # self.status = kwargs.pop("status")
        