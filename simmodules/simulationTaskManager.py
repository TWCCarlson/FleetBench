import pprint
pp = pprint.PrettyPrinter(indent=4)
import logging

class simTaskManager:
    def __init__(self, parent):
        self.parent = parent

        # Data structures
        self.taskList = {}

        logging.debug("Class 'simTaskManager' initialized.")

    def buildReferences(self):
        # Build references to objects declared after this one
        self.simAgentManager = self.parent.simAgentManager
        self.simTaskManager = self.parent.simTaskManager
        self.simProcessor = self.parent.simProcessor

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

        # Update the treeView
        self.parent.parent.simulationWindow.simDataView.updateTaskTreeView()

    def fixAssignments(self):
        # Iterate through the list of all tasks, fixing assignee to refer to objects instead of IDs
        # Needed to overcome pickling of data when retrieving the state
        for task in self.taskList:
            if not self.taskList[task].assignee == None:
                self.taskList[task].assignee = self.parent.simAgentManager.agentList[self.taskList[task].assignee]

    def retrieveInitialSimState(self):
        # Extract the data from the session edit window data
        dataPackage = self.parent.parent.parent.taskManager.packageTaskData()
        # Reconstruct the tasks from the data
        for task in dataPackage:
            taskName = dataPackage[task]["name"]
            pickupPosition = dataPackage[task]["pickupPosition"]
            dropoffPosition = dataPackage[task]["dropoffPosition"]
            timeLimit = dataPackage[task]["timeLimit"]
            if "assignee" in dataPackage[task]:
                assignee = dataPackage[task]["assignee"]
            else:
                assignee = None
            self.createNewTask(
                taskName=taskName,
                pickupPosition=pickupPosition,
                dropoffPosition=dropoffPosition,
                timeLimit=timeLimit,
                assignee=assignee
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
        self.numID = kwargs.get("numID")        # Numeric ID, internal use only
        self.name = kwargs.get("taskName")      # Human-readable ID, name
        self.pickupPosition = kwargs.get("pickupPosition")      # Expects Tuple
        self.dropoffPosition = kwargs.get("dropoffPosition")    # Expects Tuple
        self.timeLimit = kwargs.get("timeLimit")
        self.pickupNode = f"({self.pickupPosition[0]}, {self.pickupPosition[1]})"
        self.dropoffNode = f"({self.dropoffPosition[0]}, {self.dropoffPosition[1]})"
        self.assignee = kwargs.get("assignee")

    def highlightTask(self, multi):
        # Hightlight the pickup position
        logging.debug(f"Task '{self.name}:{self.numID}' requests highlighting from 'mainCanvas'.")
        self.parent.parent.parent.simulationWindow.simMainView.simCanvas.highlightTile(self.pickupPosition[0], self.pickupPosition[1], 'green', multi=multi, highlightType='pickupHighlight')
        self.parent.parent.parent.simulationWindow.simMainView.simCanvas.highlightTile(self.dropoffPosition[0], self.dropoffPosition[1], 'blue', multi=multi, highlightType='dropoffHighlight')