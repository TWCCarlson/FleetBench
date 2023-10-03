import logging
import copy
import pprint
pp = pprint.PrettyPrinter(indent=4)
import networkx as nx

from heapq import heappop, heappush
from itertools import count
from numpy import inf
from numpy import sqrt
import time

class simAgentManager:
    def __init__(self, parent):
        self.parent = parent

        # Data structures
        self.agentList = {}

        logging.debug("Class 'simAgentManager' initialized.")

    def buildReferences(self):
        # Build references to objects declared after this one
        self.simAgentManager = self.parent.simAgentManager
        self.simTaskManager = self.parent.simTaskManager
        self.simProcessor = self.parent.simProcessor
        self.simMainView = self.parent.parent.simulationWindow.simMainView

    def createNewAgent(self, **kwargs):
        """
            Create a new instance of the Agent class, using collected properties
            Used when loading in simulation data
            Inputs:
                - ID: Human-readable name
                - position: Node within the graph
                - orientation: Direction the agent faces
                - className: Agent type
        """
        logging.debug(f"Simulation received request for new agent:")
        logging.debug(f"{kwargs}")
        self.dictLength = len(self.agentList)
        ID = kwargs.pop("ID")

        # If there is a need for an automatically generated name
        if ID == "ag":
            ID = str(self.dictLength)
            logging.debug(f"Reques does not contain an ID. Agent was automatically assigned ID '{ID}'") 
        
        # Create a new agent and add it to the manager's list
        self.latestAgent = simAgentClass(self, **kwargs, ID=ID, numID=self.dictLength)
        self.agentList[self.dictLength] = self.latestAgent

        # Insert the agent into the simulation map data
        self.parent.simGraphData.updateAgentLocations(self.agentList)
        logging.info(f"Agent added to the dict of agents")

        # Update the treeView
        self.parent.parent.simulationWindow.simDataView.updateAgentTreeView()

    def fixAssignments(self):
        # Iterate through the list of all agents, fixing currenTask to refer to objects instead of IDs
        # Needed to overcome pickling of data when retrieving the state
        for agent in self.agentList:
            if not self.agentList[agent].currentTask == None:
                # print(self.agentList)
                # print(self.simTaskManager.taskList)
                self.agentList[agent].currentTask = self.simTaskManager.taskList[self.agentList[agent].currentTask]

    def pushDataToCanvas(self):
        self.parent.parent.simulationWindow.simMainView.simCanvas.ingestAgentData(self)

    def retrieveInitialSimState(self):
        # Extract the data from the session edit window data
        dataPackage = self.parent.parent.parent.agentManager.packageAgentData()
        # Populate the agent condition into the 
        for agent in dataPackage:
            ID = dataPackage[agent]["ID"]
            position = dataPackage[agent]["position"]
            orientation = dataPackage[agent]["orientation"]
            className = dataPackage[agent]["className"]
            if "currentTask" in dataPackage[agent]:
                currentTask = dataPackage[agent]["currentTask"]
                taskStatus = "retrieving"
            else:
                currentTask = None
            self.createNewAgent(
                ID=ID, 
                position=position, 
                orientation=orientation, 
                className=className,
                currentTask=currentTask,
                taskStatus=taskStatus
                )
        logging.info("All agents ported from main session state into simulation state.")

class simAgentClass:
    """
        Agent class
    """
    def __init__(self, parent, **kwargs):
        self.parent = parent
        logging.info(f"New 'simAgentClass' instantiated.")
        logging.debug(f"Agent settings: {kwargs}")
        self.numID = kwargs.get("numID")    # Numeric ID, internal use
        self.ID = kwargs.get("ID")          # Human-readable ID, name
        self.position = kwargs.get("position")
        self.currentNode = f"({self.position[0]}, {self.position[1]})"
        self.orientation = kwargs.get("orientation")
        self.className = kwargs.get("className")
        self.currentTask = kwargs.get("currentTask")
        self.taskStatus = kwargs.get("taskStatus")
        self.pathfinder = None

        # Build useful references
        self.mapGraphRef = self.parent.parent.simGraphData.simMapGraph
        pp.pprint(self.mapGraphRef)
        self.mainViewRef = self.parent.parent.parent.simulationWindow.simMainView

        # Dict of directions and their numerical values
        # Used for rotation + = CCW, - = CW
        self.dirDict = {
            "N" : 0,
            "W" : 1,
            "S" : 2,
            "E" : 3
        }

    def taskInteraction(self, targetNode):
        # Called when the agent is sharing a node with its task target node
        if self.currentNode == targetNode:
            targetNodeIDDict = {
                self.currentTask.pickupNode: "pickup",
                self.currentTask.dropoffNode: "dropoff"
            }
            action = targetNodeIDDict[targetNode]

            if action == "pickup":
                # Update task status fields
                self.taskStatus = "pickedUp"
                self.currentTask.taskStatus = "pickedUp"
            elif action == "dropoff":
                self.taskStatus = "droppedOff"
                self.currentTask.taskStatus = "droppedOff"
                self.currentTask = None

    def returnTargetNode(self):
        # Called to determine the target node for pathfinding, dependant on task status
        taskStatusMapping = {
            "retrieving": self.currentTask.pickupNode,
            "pickedUp": self.currentTask.dropoffNode
        }
        targetNode = taskStatusMapping[self.taskStatus]
        return targetNode

    def highlightAgent(self, multi):
        # Have the agent request highlighting from the main canvas
        logging.debug(f"Agent '{self.ID}:{self.numID}' requests highlighting from 'mainCanvas'.")
        self.mainViewRef.simCanvas.requestRender("highlight", "new", {"targetNodeID": self.position,
                "highlightType": "agentHighlight", "multi": False, "highlightTags": ["agent"+str(self.numID)+"Highlight"]})
        self.mainViewRef.simCanvas.handleRenderQueue()

    def calculateAStarBestPathLength(self, targetNode):
        bestAStarPathLength = nx.astar_path_length(self.mapGraphRef, self.currentNode, targetNode, heuristic=None, weight=None)
        logging.debug(f"Agent '{self.ID}:{self.numID}' A* Calculates a path of length {bestAStarPathLength} from {self.position} to {targetNode}")
        return bestAStarPathLength
    
    def calculateAStarBestPath(self, targetNode):
        bestAStarPath = nx.astar_path(self.mapGraphRef, self.currentNode, targetNode, heuristic=None, weight=None)
        logging.debug(f"Agent 'Agent '{self.ID}:{self.numID}' A* Calculates a path from {self.position} to {targetNode} of: \n{bestAStarPath}") 
        return bestAStarPath
    
    def findAllSimplePathsOfCutoffK(self, targetNode, cutoffLength):
        logging.debug(f"Agent '{self.ID}:{self.numID}' attempting to find all paths up to length {cutoffLength} . . .")
        cutoffKPathsGenerator = nx.all_simple_paths(self.mapGraphRef, self.currentNode, targetNode, cutoffLength)
        logging.debug(f"Found paths:")
        cutoffKPathsList = list(cutoffKPathsGenerator)
        for count, path in enumerate(cutoffKPathsList):
            logging.debug(f"{count}: {path}")
        
        return cutoffKPathsList
    
    def calculateAStarPath(self, sourceNode, targetNode, heuristic="Dijkstra"):
        # Seek the shortest path between the targetNode and agent's currentNode
        # Account for obstacles (other agents)
        # Heuristic a choice between Manhattan and Euclidean
        if sourceNode not in self.mapGraphRef or targetNode not in self.mapGraphRef:
            msg = f"Either source {sourceNode} or target {targetNode} is not in graph."
            raise nx.NodeNotFound(msg)
        
        # Heuristic accepts two nodes and calculates a "distance" estimate that must be admissible
        if heuristic == "Dijkstra":
            def heuristic(u, v):
                # Dijkstra's always underestimates, making it admissible, but does nothing to speed up pathfinding
                return 0
        elif heuristic == "Manhattan":
            def heuristic(u, v):
                # Manhattan/taxicab distance is the absolute value of the difference 
                uPos = self.mapGraphRef.nodes[u]['pos']
                vPos = self.mapGraphRef.nodes[v]['pos']
                heuristicDistance = abs(uPos['X']-vPos['X']) + abs(uPos['Y']-vPos['Y'])
                return heuristicDistance
        elif heuristic == "Euclidean":
            def heuristic(u, v):
                # Euclidean/rectilinear/pythagoras distance is line length between two points
                uPos = self.mapGraphRef.nodes[u]['pos']
                vPos = self.mapGraphRef.nodes[v]['pos']
                heuristicDistance = sqrt((uPos['X']-vPos['X'])**2 + (uPos['Y']-vPos['Y'])**2)
                return heuristicDistance
        elif heuristic == "Approx. Euclidean":
            def heuristic(u, v):
                # An approximation of euclidean distance
                uPos = self.mapGraphRef.nodes[u]['pos']
                vPos = self.mapGraphRef.nodes[v]['pos']
                delta_1 = abs(uPos['X']-vPos['X'])
                delta_2 = abs(uPos['Y']-vPos['Y'])
                b = max(delta_1, delta_2)
                a = min(delta_1, delta_2)
                heuristicDistance = b + 0.428 * a * a / b
                return heuristicDistance
        
        # All edges in the graph should have a weight of "1"
        # Therefore there is no need to calculate the weights, as neighborliness is assured by .items()
        push = heappush
        pop = heappop
        weight = 1

        # gScore is the distance from source to current node
        gScore = {}
        # fScore is the distance from source to target through current node
        fScore = {}
        # cameFrom holds the optimal previous node on the path to the current node
        cameFrom = {}

        # The openset, populated with the first node
        # The heap queue pulls the smallest item from the heap
        # The first element in the format is the fScore, minimizing this is an objective
        # The second element is a counter, used to break ties in the fScore
        counter = count()
        openSet = []

        # Initialize the starting node into the queue, alongside its appropriate maps
        heappush(openSet, (0, next(counter), sourceNode))
        gScore[sourceNode] = 0
        fScore[sourceNode] = heuristic(sourceNode, targetNode)

        # Recursively work through the queue
        while openSet:
            _, __, currentNode = pop(openSet)
            if currentNode == targetNode:
                # Return successfully, with the reconstructed path if the currentNode is the targetNode
                path = [currentNode]
                parentNode = cameFrom.get(currentNode, None)
                while parentNode is not None:
                    path.append(parentNode)
                    parentNode = cameFrom.get(parentNode, None)
                # Reverse the path to get the route from source to target
                path.reverse()
                return path
            
            for neighborNode, data in self.mapGraphRef[currentNode].items():
                est_gScore = gScore[currentNode] + weight
                # If this estimated gScore for the neighbor is less than the currently mapped one
                if est_gScore < gScore.get(neighborNode, inf):
                    # Then a new best path has been found to reach the neighbor node
                    cameFrom[neighborNode] = currentNode
                    # Record its new gScore
                    gScore[neighborNode] = est_gScore       
                    # Calculate the fScore for the neighbor node
                    node_fScore = est_gScore + heuristic(currentNode, targetNode)             
                    # If the node isn't already in the openSet, add it
                    if neighborNode not in fScore:
                        push(openSet, (node_fScore, next(counter), neighborNode))
                    # Update the fScore of the neighbor node
                    fScore[neighborNode] = node_fScore

        raise nx.NetworkXNoPath(f"Node {targetNode} not reachable from {sourceNode}")
    
    def showCalculatingAStarPath(self, sourceNode, targetNode, firstIterBool, heuristic="Dijkstra"):
        # Seek the shortest path between the targetNode and agent's currentNode
        # Render each step to visualize the process
        
        # Account for obstacles (other agents)
        if firstIterBool:
            # Heuristic a choice between Manhattan and Euclidean
            if sourceNode not in self.mapGraphRef or targetNode not in self.mapGraphRef:
                msg = f"Either source {sourceNode} or target {targetNode} is not in graph."
                raise nx.NodeNotFound(msg)
            
            # Heuristic accepts two nodes and calculates a "distance" estimate that must be admissible
            if heuristic == "Dijkstra":
                def heuristic(u, v):
                    # Dijkstra's always underestimates, making it admissible, but does nothing to speed up pathfinding
                    return 0
            elif heuristic == "Manhattan":
                def heuristic(u, v):
                    # Manhattan/taxicab distance is the absolute value of the difference 
                    uPos = self.mapGraphRef.nodes[u]['pos']
                    vPos = self.mapGraphRef.nodes[v]['pos']
                    heuristicDistance = abs(uPos['X']-vPos['X']) + abs(uPos['Y']-vPos['Y'])
                    return heuristicDistance
            elif heuristic == "Euclidean":
                def heuristic(u, v):
                    # Euclidean/rectilinear/pythagoras distance is line length between two points
                    uPos = self.mapGraphRef.nodes[u]['pos']
                    vPos = self.mapGraphRef.nodes[v]['pos']
                    heuristicDistance = sqrt((uPos['X']-vPos['X'])**2 + (uPos['Y']-vPos['Y'])**2)
                    return heuristicDistance
            elif heuristic == "Approx. Euclidean":
                def heuristic(u, v):
                    # An approximation of euclidean distance
                    uPos = self.mapGraphRef.nodes[u]['pos']
                    vPos = self.mapGraphRef.nodes[v]['pos']
                    delta_1 = abs(uPos['X']-vPos['X'])
                    delta_2 = abs(uPos['Y']-vPos['Y'])
                    b = max(delta_1, delta_2)
                    a = min(delta_1, delta_2)
                    heuristicDistance = b + 0.428 * a * a / b
                    return heuristicDistance
            
            # All edges in the graph should have a weight of "1"
            # Therefore there is no need to calculate the weights, as neighborliness is assured by .items()
            push = heappush
            pop = heappop
            weight = 1

            # gScore is the distance from source to current node
            gScore = {}
            # fScore is the distance from source to target through current node
            fScore = {}
            # cameFrom holds the optimal previous node on the path to the current node
            cameFrom = {}

            # The openset, populated with the first node
            # The heap queue pulls the smallest item from the heap
            # The first element in the format is the fScore, minimizing this is an objective
            # The second element is a counter, used to break ties in the fScore
            counter = count()
            openSet = []

            # Initialize the starting node into the queue, alongside its appropriate maps
            heappush(openSet, (0, next(counter), sourceNode))
            gScore[sourceNode] = 0
            fScore[sourceNode] = heuristic(sourceNode, targetNode)

        # Recursively work through the queue
        if openSet:
            _, __, currentNode = pop(openSet)
            if currentNode == targetNode:
                # Return successfully, with the reconstructed path if the currentNode is the targetNode
                path = [currentNode]
                parentNode = cameFrom.get(currentNode, None)
                while parentNode is not None:
                    path.append(parentNode)
                    parentNode = cameFrom.get(parentNode, None)
                # Reverse the path to get the route from source to target
                path.reverse()
                return path
            
            for neighborNode, data in self.mapGraphRef[currentNode].items():
                est_gScore = gScore[currentNode] + weight
                # If this estimated gScore for the neighbor is less than the currently mapped one
                if est_gScore < gScore.get(neighborNode, inf):
                    # Then a new best path has been found to reach the neighbor node
                    cameFrom[neighborNode] = currentNode
                    # Record its new gScore
                    gScore[neighborNode] = est_gScore       
                    # Calculate the fScore for the neighbor node
                    node_fScore = est_gScore + heuristic(currentNode, targetNode)             
                    # If the node isn't already in the openSet, add it
                    if neighborNode not in fScore:
                        push(openSet, (node_fScore, next(counter), neighborNode))
                    # Update the fScore of the neighbor node
                    fScore[neighborNode] = node_fScore
        else:
            raise nx.NetworkXNoPath(f"Node {targetNode} not reachable from {sourceNode}")
        return None

    def validateCandidateMove(self, targetNode):
        """
            Used to check whether an agent can move to a target node
            - There must be an edge between current node and target node
            - There cannot be an agent in the target node, if the config specifies no agent overlap
        """
        currentNode = self.currentNode
        if isinstance(targetNode, str):
            targetNode = targetNode
        elif isinstance(targetNode, tuple):
            targetNode = f"({targetNode[0]}, {targetNode[1]})"
        
        logging.debug(f"Checking if currentNode '{currentNode}' and targetNode '{targetNode}' share an edge . . .")
        if not self.mapGraphRef.has_edge(currentNode, targetNode):
            logging.debug("Edge does not exist.")
            return False
        logging.debug("Edge exists.")

        logging.debug(f"Checking if targetNode '{targetNode}' is occupied by an agent . . .")
        if 'agent' in self.mapGraphRef.nodes(data=True)[targetNode]:
            logging.debug(f"TargetNode '{targetNode}' contains an agent. Cannot move here.")
            return False
        logging.debug("Node has space to be moved into.")
        
        return True
    
    def executeMove(self, targetNode):
        """
            Move the agent to the targetNode, to be done only after the move is valid
        """
        logging.debug(f"Moving agent '{self.ID}' to node '{targetNode}'")
        self.mainViewRef.simCanvas.requestRender("agent", "move", {"agentNumID": self.numID, "sourceNodeID": self.currentNode, "targetNodeID": targetNode})
        self.mainViewRef.simCanvas.handleRenderQueue()
        if isinstance(targetNode, str):
            self.currentNode = targetNode    # String
            self.position = eval(targetNode) # Tuple
        elif isinstance(targetNode, tuple):
            self.position = targetNode
            self.currentNode = f"({targetNode[0]}, {targetNode[1]})"
        else:
            logging.error(f"Received invalid targetNode type: {type(targetNode)}")
            raise TypeError

        # Update the mapgraph with the new location
        self.parent.parent.simGraphData.updateAgentLocations(self.parent.agentList)