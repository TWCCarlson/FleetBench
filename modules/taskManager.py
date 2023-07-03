import networkx as nx
import pprint
import modules.exceptions as RWSE
import random
pp = pprint.PrettyPrinter(indent=4)

class taskManager:
    """
        Class which manages the information pertaining to task existence and activity
    """
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
        self.dictLength = len(self.taskList)
        try:
            taskName = kwargs.pop("taskName")
        except KeyError:
            taskName = self.dictLength
        print(taskName)
        self.latestTask = taskClass(self, **kwargs, taskName=taskName, numID=self.dictLength)
        self.taskList[self.dictLength] = self.latestTask
        print(self.taskList)

        # Update the treeview
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
        dataPackage = {}
        for task in self.taskList:
            pp.pprint(self.taskList[task])
            taskData = {
                "name": self.taskList[task].name,
                "pickupPosition": self.taskList[task].pickupPosition,
                "dropoffPosition": self.taskList[task].dropoffPosition,
                "timeLimit": self.taskList[task].timeLimit
            }
            dataPackage[self.taskList[task].numID] = taskData
        pp.pprint(dataPackage)
        return dataPackage
    
    def generateRandomTask(self, respectNodeTypes):
        print("Generating random task")
        print(respectNodeTypes)

        # Find a node from which the task can begin ('pickup')
        if self.parent.toolBar.taskGeneratorRespectsNodeTypes == True:
            # Restrict the node options to those which have the node 'type' attribute 'Pickup'
            nodeOptions = [node for node, attributes in self.parent.mapData.mapGraph.nodes(data=True) if attributes['type']=='pickup']
            randomPickupNode = self.parent.randomGenerator.randomChoice(nodeOptions)
            print(f"Node chosen from pickup nodes only: {randomPickupNode}")
        elif self.parent.toolBar.taskGeneratorRespectsNodeTypes == False:
            # Choose any node
            nodeOptions = list(self.parent.mapData.mapGraph.nodes())
            randomPickupNode = self.parent.randomGenerator.randomChoice(nodeOptions)
            print(f"Node chosen from all nodes ignoring type: {randomPickupNode}")
        pickupNodeData = self.parent.mapData.mapGraph.nodes(data=True)[randomPickupNode]
        pickupPosition = (pickupNodeData['pos']['X'], pickupNodeData['pos']['Y'])
        print(pickupPosition)

        # Find all nodes it can access that are valid task endpoints ('deposit')
        if self.parent.toolBar.taskGeneratorRespectsNodeTypes == True:
            # Restrict the node options to those which have the node 'type' attribute 'deposit'
            nodeOptions = [node for node, attributes in self.parent.mapData.mapGraph.nodes(data=True) if attributes['type']=='deposit']
            randomDropoffNode = self.parent.randomGenerator.randomChoice(nodeOptions)
            print(f"Node chosen from dropoff nodes only: {randomDropoffNode}")
        elif self.parent.toolBar.taskGeneratorRespectsNodeTypes == False:
            # Choose any node
            nodeOptions = list(self.parent.mapData.mapGraph.nodes())
            randomDropoffNode = self.parent.randomGenerator.randomChoice(nodeOptions)
            # Catch the case where dropoff could end up being the same as pickup
            while randomDropoffNode == randomPickupNode:
                randomDropoffNode = self.parent.randomGenerator.randomChoice(nodeOptions)
            print(f"Node chosen from all nodes ignoring type: {randomDropoffNode}")
        dropoffNodeData = self.parent.mapData.mapGraph.nodes(data=True)[randomDropoffNode]
        dropoffPosition = (dropoffNodeData['pos']['X'], dropoffNodeData['pos']['Y'])
        print(dropoffPosition)

        # Create the new task with the randomly generated positions
        self.createNewTask(pickupPosition=pickupPosition, dropoffPosition=dropoffPosition, timeLimit=0)

class taskClass:
    """
        Task class, contains descriptive information and methods
    """
    def __init__(self, parent, **kwargs):
        self.parent = parent
        print("Create Task")
        self.numID = kwargs.pop("numID")
        self.name = kwargs.pop("taskName")
        self.pickupPosition = kwargs.pop("pickupPosition")      # Expects Tuple
        self.dropoffPosition = kwargs.pop("dropoffPosition")    # Expects Tuple
        self.timeLimit = kwargs.pop("timeLimit")
        self.pickupNode = f"({self.pickupPosition[0]}, {self.pickupPosition[1]})"
        self.dropoffNode = f"({self.dropoffPosition[0]}, {self.dropoffPosition[1]})"
        self.graphRef = self.parent.parent.mapData.mapGraph
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
        print(f"Dijkstra Calculates a path of length {bestDijkstraPathLength}")
        return bestDijkstraPathLength

    def calculateAStarBestPath(self):
        bestAStarPathLength = nx.astar_path_length(self.graphRef, self.pickupNode, self.dropoffNode, heuristic=None, weight=None)
        print(f"A* Calculates a path of length {bestAStarPathLength}")

    def calculateRankedShortestSimplePaths(self):
        shortestPathsList = nx.shortest_simple_paths(self.graphRef, self.pickupNode, self.dropoffNode)
        print(list(shortestPathsList))
        for i, path in enumerate(shortestPathsList):
            # Subtract 1 because we are counting nodes which includes the start position
            # Interested inthe number of 'steps' to reach the target
            print(f"Path {i} has length {len(path)-1}")
