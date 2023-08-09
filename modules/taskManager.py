import networkx as nx
import pprint
import modules.exceptions as RWSE
import tkinter as tk
import logging
pp = pprint.PrettyPrinter(indent=4)

class taskManager:
    """
        Class which manages the information pertaining to task existence and activity
    """
    def __init__(self, parent):
        logging.debug("taskManager data class initializing . . .")
        self.parent = parent
        # Generates tasks
        # A task contains
        # Pickup loc, dropoff loc, optimal time to complete, maximum time before failure, status
        # Leave room for misc details (weight, etc)
        # Each task should be an instance of a task class
        self.taskList = {}
        self.taskPositionList = {}
        self.currentTask = []
        logging.info("Task manager initialized.")
        
    def createNewTask(self, **kwargs):
        """
            Create a new instance of the Task class, using collected properties from the generation UI
            Also used when loading in saved data
            Inputs:
                - taskName: 'Human-readable' name of the task
                - pickupPosition: Node in the graph at which the task begins
                - dropoffPosition: Node in the graph at which the task ends
                - timeLimit: The amount of simulation steps before the task is considered overdue
        """
        # The length of a dict is always 1 higher than the numeric id
        logging.info(f"Received request for new task.")
        logging.debug(f"Request settings: {kwargs}")
        self.dictLength = len(self.taskList)
        try:
            taskName = kwargs.pop("taskName")
        except KeyError:
            taskName = str(self.dictLength)
        self.latestTask = taskClass(self, **kwargs, taskName=taskName, numID=self.dictLength)
        self.taskList[self.dictLength] = self.latestTask
        logging.info("Task added to taskManager taskList.")

        # Update the treeview
        logging.debug(f"Requesting update to taskTreeView with new taskList . . .")
        self.parent.contextView.updateTaskTreeView()

    def deleteTask(self, taskName=None, taskID=None):
        """
            Irrevocably delete an agent from the list. This results in data loss and should only be used to remove agents that shouldn't have been made in th efirst place.
        """
        logging.debug(f"Received request to delete task '{taskName}:{taskID}' . . .")
        # If the internal ID of the agent is supplied, it can be deleted from the dict directly
        if taskID: targetTask = taskID
        # If the human-readable name of the agent is supplied, the attribute needs to be searched for first
        if taskName: targetTask = [taskID for taskID in list(self.taskList) if self.taskList[taskID].name == taskName][0]

        # First verify the user actually wants to do this
        targetTaskName = self.taskList[targetTask].name
        targetTaskID = self.taskList[targetTask].numID
        deletionPrompt = tk.messagebox.askokcancel(title="Are you sure?", message=f"You are about to delete task '{self.taskList[targetTask].name}' from the simulation. \n\nAre you sure?")

        if deletionPrompt:
            logging.debug(f"User verified deletion of task: '{targetTaskName}:{targetTaskID}'")
            del self.taskList[targetTask]
        else:
            logging.debug(f"User cancelled deteletion of task.")
            return

        # Redraw the agent treeview
        self.parent.contextView.updateTaskTreeView()
        self.parent.mainView.mainCanvas.renderGraphState()
        logging.info(f"Task '{targetTaskName}:{targetTaskID}' successfully deleted.")

    def assignAgentToTask(self):
        # Retrieve the managed agent and target task IDs
        agentRef = self.parent.agentManager.currentAgent
        taskRef = self.currentTask

        # Assign the agent to the task
        taskRef.assignee = agentRef

        # Update the task treeView to reflect the changes
        self.parent.contextView.updateTaskTreeView()

        # # Assign the task to the agent
        # self.parent.agentManager.agentList[agentRef.numID].currentTask = taskRef

    def fixAssignments(self):
        # Iterate through the list of all tasks, fixing assignee to refer to objects instead of IDs
        for task in self.taskList:
            if not self.taskList[task].assignee == None:
                self.taskList[task].assignee = self.parent.agentManager.agentList[self.taskList[task].assignee]

        # Update the treeView to reflect the change
        self.parent.contextView.updateTaskTreeView()

    def packageTaskData(self):
        """
            Package reconstruction data for replicating the current state of the task manager
            This means the data needed to create each task needs to be available to each call to createNewTask
                - Task Name
                - Pickup Node
                - Dropoff Node
                - Time Limit
        """
        logging.info("Received request to package 'taskManager' data.")
        dataPackage = {}
        for task in self.taskList:
            # Pull agent info for reconstruction
            if self.taskList[task].assignee:
                assignee = self.taskList[task].assignee.numID
            else:
                assignee = None

            taskData = {
                "name": self.taskList[task].name,
                "pickupPosition": self.taskList[task].pickupPosition,
                "dropoffPosition": self.taskList[task].dropoffPosition,
                "timeLimit": self.taskList[task].timeLimit,
                "assignee": assignee
            }
            dataPackage[self.taskList[task].numID] = taskData
            logging.debug(f"Packaged taskData: {taskData}")
        logging.info("Packaged all 'taskManager' data.")
        return dataPackage
    
    def generateRandomTask(self, respectNodeTypes):
        logging.info(f"Received request to generate new randomized task.")
        logging.debug(f"Randomized task should respect node types: '{bool(respectNodeTypes)}'")

        # Find a node from which the task can begin ('pickup')
        if self.parent.toolBar.taskGeneratorRespectsNodeTypes == True:
            # Restrict the node options to those which have the node 'type' attribute 'Pickup'
            nodeOptions = [node for node, attributes in self.parent.mapData.mapGraph.nodes(data=True) if attributes['type']=='pickup']
            randomPickupNode = self.parent.randomGenerator.randomChoice(nodeOptions)
            # print(f"Node chosen from pickup nodes only: {randomPickupNode}")
        elif self.parent.toolBar.taskGeneratorRespectsNodeTypes == False:
            # Choose any node
            nodeOptions = list(self.parent.mapData.mapGraph.nodes())
            randomPickupNode = self.parent.randomGenerator.randomChoice(nodeOptions)
            # print(f"Node chosen from all nodes ignoring type: {randomPickupNode}")
        pickupNodeData = self.parent.mapData.mapGraph.nodes(data=True)[randomPickupNode]
        pickupPosition = (pickupNodeData['pos']['X'], pickupNodeData['pos']['Y'])
        logging.debug(f"Randomly selected pickupNode: {pickupPosition}:{pickupNodeData}")

        # Find all nodes it can access that are valid task endpoints ('deposit')
        if self.parent.toolBar.taskGeneratorRespectsNodeTypes == True:
            # Restrict the node options to those which have the node 'type' attribute 'deposit'
            nodeOptions = [node for node, attributes in self.parent.mapData.mapGraph.nodes(data=True) if attributes['type']=='deposit']
            randomDropoffNode = self.parent.randomGenerator.randomChoice(nodeOptions)
            # print(f"Node chosen from dropoff nodes only: {randomDropoffNode}")
        elif self.parent.toolBar.taskGeneratorRespectsNodeTypes == False:
            # Choose any node
            nodeOptions = list(self.parent.mapData.mapGraph.nodes())
            randomDropoffNode = self.parent.randomGenerator.randomChoice(nodeOptions)
            # Catch the case where dropoff could end up being the same as pickup
            while randomDropoffNode == randomPickupNode:
                randomDropoffNode = self.parent.randomGenerator.randomChoice(nodeOptions)
            # print(f"Node chosen from all nodes ignoring type: {randomDropoffNode}")
        dropoffNodeData = self.parent.mapData.mapGraph.nodes(data=True)[randomDropoffNode]
        dropoffPosition = (dropoffNodeData['pos']['X'], dropoffNodeData['pos']['Y'])
        logging.debug(f"Randomly selected dropoffNode: {dropoffPosition}:{dropoffNodeData}")

        # Create the new task with the randomly generated positions
        logging.info(f"Random task generation settings selected.")
        self.createNewTask(pickupPosition=pickupPosition, dropoffPosition=dropoffPosition, timeLimit=0)

class taskClass:
    """
        Task class, contains descriptive information and methods
    """
    def __init__(self, parent, **kwargs):
        self.parent = parent
        logging.info("New 'taskClass' instantiated.")
        logging.debug(f"Task settings: {kwargs}")
        self.numID = kwargs.get("numID")    # Numeric ID, internal use only
        self.name = kwargs.get("taskName")  # Human-readable ID, name
        self.pickupPosition = kwargs.get("pickupPosition")      # Expects Tuple
        self.dropoffPosition = kwargs.get("dropoffPosition")    # Expects Tuple
        self.timeLimit = kwargs.get("timeLimit")
        self.pickupNode = f"({self.pickupPosition[0]}, {self.pickupPosition[1]})"
        self.dropoffNode = f"({self.dropoffPosition[0]}, {self.dropoffPosition[1]})"
        self.graphRef = self.parent.parent.mapData.mapGraph
        self.assignee = kwargs.get("assignee")
        # self.status = kwargs.pop("status")
        # Verify that the task is completable (no obstacles considered)
        # try:
        # Calculate the minimum time to complete, assuming picking up the item and dropping it off takes 1 "step"
        self.minTimeToComplete = self.calculateShortest_Path() + 2
        if self.minTimeToComplete > self.timeLimit and self.timeLimit != 0:
            raise RWSE.RWSTaskTimeLimitImpossible(timeLimit=self.timeLimit, minTimeToComplete=self.minTimeToComplete)

        # self.calculateAStarBestPath()
        # self.calculateRankedShortestSimplePaths()

    def highlightTask(self, multi):
        # Hightlight the pickup position
        logging.debug(f"Task '{self.name}:{self.numID}' requests highlighting from 'mainCanvas'.")
        self.parent.parent.mainView.mainCanvas.highlightTile(self.pickupPosition[0], self.pickupPosition[1], 'green', multi=multi, highlightType='pickupHighlight')
        self.parent.parent.mainView.mainCanvas.highlightTile(self.dropoffPosition[0], self.dropoffPosition[1], 'blue', multi=multi, highlightType='dropoffHighlight')

    # Pathfinding
    # It may be better to have the central AI compute all shortest paths and have agents reference a dict
    # Would increase speed significantly to do hashtable lookups with that data
    # But we want the nth-best paths too, TODO
    # For now, implement methods to fire the best path calculations
    # https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html
    def calculateShortest_Path(self):
        # Uses dijkstra anyways
        bestShortest_Path = nx.shortest_path_length(self.graphRef, self.pickupNode, self.dropoffNode)
        bestDijkstraPathLength = nx.dijkstra_path_length(self.graphRef, self.pickupNode, self.dropoffNode)
        logging.debug(f"{self.name}:{self.numID} Dijkstra Calculates a path of length {bestDijkstraPathLength}")
        return bestDijkstraPathLength

    def calculateAStarBestPath(self):
        bestAStarPathLength = nx.astar_path_length(self.graphRef, self.pickupNode, self.dropoffNode, heuristic=None, weight=None)
        logging.debug(f"{self.name}:{self.numID} A* Calculates a path of length {bestAStarPathLength}")

    def calculateRankedShortestSimplePaths(self):
        logging.info("Seeking a list of all shortest paths.")
        shortestPathsList = nx.shortest_simple_paths(self.graphRef, self.pickupNode, self.dropoffNode)
        # print(list(shortestPathsList))
        for i, path in enumerate(shortestPathsList):
            # Subtract 1 because we are counting nodes which includes the start position
            # Interested inthe number of 'steps' to reach the target
            # print(f"Path {i} has length {len(path)-1}")
            logging.debug(f"Path {i} has length {len(path)-1}")
