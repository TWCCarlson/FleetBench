import networkx as nx

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
        self.pickupNode = f"({self.pickupPosition[0]}, {self.pickupPosition[1]})"
        self.dropoffNode = f"({self.dropoffPosition[0]}, {self.dropoffPosition[1]})"
        self.graphRef = self.parent.parent.mapData.mapGraph
        # self.status = kwargs.pop("status")
        self.calculateShortest_Path()
        self.calculateAStarBestPath()
        self.calculateRankedShortestSimplePaths()

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