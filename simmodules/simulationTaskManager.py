import pprint
pp = pprint.PrettyPrinter(indent=4)
import logging

class simTaskManager:
    def __init__(self, parent):
        self.parent = parent

        # Data structures
        self.taskList = {}

        # Retrieve initial simulation state from the main window task manager
        self.retrieveInitialSimState()
        logging.debug("Class 'simTaskManager' initialized.")

    def createNewTask(self, **kwargs):
        """
            Create a new instance of the task class using collected properties
            Used when loading in simulation data
            Inputs:
                - taskName: Human-readable name of the task
                - pickupPosition: Node in the graph where the task begins
                - dropoffPosition: Node in the graph where the task ends
                - timeLimit: Simulation step count before task is overdue
        """
        logging.debug("Simulation receive request for new task:")
        logging.debug(f"{kwargs}")
        self.dictLength = len(self.taskList)
        try:
            taskName = kwargs.pop("taskName")
        except KeyError:
            taskName = str(self.dictLength)
        self.latestTask = simTaskClass(self, **kwargs, taskName=taskName, numID=self.dictLength)
        self.taskList[self.dictLength] = self.latestTask
        logging.info("Task added to 'simTaskManager' task list.")

    def retrieveInitialSimState(self):
        # Extract the data from the session edit window data
        dataPackage = self.parent.parent.taskManager.packageTaskData()
        # Reconstruct the tasks from the data
        for task in dataPackage:
            taskName = dataPackage[task]["name"]
            pickupPosition = dataPackage[task]["pickupPosition"]
            dropoffPosition = dataPackage[task]["dropoffPosition"]
            timeLimit = dataPackage[task]["timeLimit"]
            self.createNewTask(
                taskName=taskName,
                pickupPosition=pickupPosition,
                dropoffPosition=dropoffPosition,
                timeLimit=timeLimit
                )
        logging.info("All task data ported to simulation state.")

class simTaskClass:
    """
        Task class
    """
    def __init__(self, parent, **kwargs):
        self.parent = parent
        logging.info("New 'simTaskClass' instantiated.")
        logging.debug(f"Task settings: {kwargs}")
        self.numID = kwargs.pop("numID")        # Numeric ID, internal use only
        self.name = kwargs.pop("taskName")      # Human-readable ID, name
        self.pickupPosition = kwargs.pop("pickupPosition")      # Expects Tuple
        self.dropoffPosition = kwargs.pop("dropoffPosition")    # Expects Tuple
        self.timeLimit = kwargs.pop("timeLimit")
        self.pickupNode = f"({self.pickupPosition[0]}, {self.pickupPosition[1]})"
        self.dropoffNode = f"({self.dropoffPosition[0]}, {self.dropoffPosition[1]})"
