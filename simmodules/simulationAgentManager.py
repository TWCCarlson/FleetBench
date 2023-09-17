import logging
import copy
import pprint
pp = pprint.PrettyPrinter(indent=4)
import networkx as nx

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

        # Build useful references
        self.mapGraphRef = self.parent.parent.simGraphData.simMapGraph

        # Dict of directions and their numerical values
        # Used for rotation + = CCW, - = CW
        self.dirDict = {
            "N" : 0,
            "W" : 1,
            "S" : 2,
            "E" : 3
        }

        # Dict that maps agent status when task is assigned to target nodes

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
        self.parent.parent.parent.simulationWindow.simMainView.simCanvas.highlightTile(
            self.position[0], self.position[1], 'green', multi=multi, highlightType='agentHighlight')

    def calculateAStarBestPath(self, targetNode):
        bestAStarPathLength = nx.astar_path_length(self.mapGraphRef, self.currentNode, targetNode, heuristic=None, weight=None)
        logging.debug(f"Agent '{self.ID}:{self.numID}' A* Calculates a path of length {bestAStarPathLength} from {self.position} to {targetNode}")
        return bestAStarPathLength
    
    def findAllSimplePathsOfCutoffK(self, targetNode, cutoffLength):
        logging.debug(f"Agent '{self.ID}:{self.numID}' attempting to find all paths up to length {cutoffLength} . . .")
        cutoffKPathsGenerator = nx.all_simple_paths(self.mapGraphRef, self.currentNode, targetNode, cutoffLength)
        logging.debug(f"Found paths:")
        cutoffKPathsList = list(cutoffKPathsGenerator)
        for count, path in enumerate(cutoffKPathsList):
            logging.debug(f"{count}: {path}")
        
        return cutoffKPathsList
        
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