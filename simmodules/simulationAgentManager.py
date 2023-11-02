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

import copy

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
            logging.debug(f"Request does not contain an ID. Agent was automatically assigned ID '{ID}'") 
        
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
        # Update the treeView
        self.parent.parent.simulationWindow.simDataView.updateAgentTreeView()

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
            renderColor = dataPackage[agent]["renderColor"]
            if "currentTask" in dataPackage[agent]:
                currentTask = dataPackage[agent]["currentTask"]
                taskStatus = dataPackage[agent]["taskStatus"]
            else:
                currentTask = None
                taskStatus = None
            self.createNewAgent(
                ID=ID, 
                position=position, 
                orientation=orientation, 
                className=className,
                currentTask=currentTask,
                taskStatus=taskStatus,
                renderColor=renderColor
                )
        logging.info("All agents ported from main session state into simulation state.")

    def loadSavedSimState(self, stateAgentData):
        for agentNumID in stateAgentData:
            # ID = stateAgentData[agent]["ID"]
            position = stateAgentData[agentNumID]["position"]
            currentNode = stateAgentData[agentNumID]["currentNode"]
            orientation = stateAgentData[agentNumID]["orientation"]
            className = stateAgentData[agentNumID]["className"]
            currentTask = stateAgentData[agentNumID]["currentTask"]
            taskStatus = stateAgentData[agentNumID]["taskStatus"]
            pathfinderData = stateAgentData[agentNumID]["pathfinder"]
            
            self.agentList[agentNumID].position = position
            self.agentList[agentNumID].currentNode = currentNode
            self.agentList[agentNumID].orientation = orientation
            self.agentList[agentNumID].className = className
            self.agentList[agentNumID].currentTask = currentTask
            self.agentList[agentNumID].taskStatus = taskStatus
            if pathfinderData is not None:
                self.agentList[agentNumID].pathfinder.__load__(pathfinderData)
            else:
                self.agentList[agentNumID].pathfinder = None
    
        # Update the treeView
        self.parent.parent.simulationWindow.simDataView.updateAgentTreeView()

        # Update agent locations in the map data
        self.parent.simGraphData.updateAgentLocations(self.agentList)

    def packageAgentData(self):
        """
            Package reconstruction data for replicating the current state of the agent manager
            This means the data needed to create each agent needs to be available to each call to createNewAgent
                - Agent Name
                - Agent position
                - Agent orientation
                - Agent Class
                - Agent's taskStatus
                - Agent's currentTask
        """
        dataPackage = {}

        # Pull all agent data
        for agentNumID in self.agentList:
            # Pull pathfinder state
            
            if self.agentList[agentNumID].pathfinder is not None:
                pathfinderData = self.agentList[agentNumID].pathfinder.__copy__()
            else:
                pathfinderData = None

            # Group the data
            agentData = {
                "ID": self.agentList[agentNumID].ID,
                "position": self.agentList[agentNumID].position,
                "currentNode": self.agentList[agentNumID].currentNode,
                "orientation": self.agentList[agentNumID].orientation,
                "className": self.agentList[agentNumID].className,
                "currentTask": self.agentList[agentNumID].currentTask,
                "taskStatus": self.agentList[agentNumID].taskStatus,
                "pathfinder": pathfinderData
            }
            dataPackage[self.agentList[agentNumID].numID] = agentData
        return dataPackage

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
        self.renderColor = kwargs.get("renderColor", None)
        self.pathfinder = None
        self.targetNode = None
        self.actionTaken = False

        # Build useful references
        self.mapGraphRef = self.parent.parent.simGraphData.simMapGraph
        self.mainViewRef = self.parent.parent.parent.simulationWindow.simMainView

        # Dict of directions and their numerical values
        # Used for rotation + = CCW, - = CW
        self.dirDict = {
            "N" : 0,
            "W" : 1,
            "S" : 2,
            "E" : 3
        }

    def taskInteraction(self, targetNode, timeStamp=None):
        # Called when the agent is sharing a node with its task target node
        if self.currentNode == targetNode and self.currentTask is not None:
            targetNodeIDDict = {
                self.currentTask.pickupNode: "pickup",
                self.currentTask.dropoffNode: "dropoff"
            }
            action = targetNodeIDDict[targetNode]

            if action == "pickup" and self.taskStatus == "retrieving":
                # Update task status fields
                self.taskStatus = "pickedUp"
                self.currentTask.taskStatus = "pickedUp"
                self.currentTask.serviceStartTime = timeStamp
                result = "pickedUp"
            elif action == "dropoff" and self.taskStatus == "pickedUp":
                self.taskStatus = "unassigned"
                self.currentTask.taskStatus = "completed"
                self.currentTask.serviceCompleteTime = timeStamp
                self.currentTask.assignee = None
                self.currentTask = None
                self.targetNode = None
                result = "completed"
        elif self.currentTask is None:
            self.targetNode = None
            # No action is needed
            return "rest"

        self.parent.parent.parent.simulationWindow.simDataView.updateAgentTreeView()
        self.parent.parent.parent.simulationWindow.simDataView.updateTaskTreeView()

        return result

    def returnTargetNode(self):
        if self.currentTask is not None:
        # Called to determine the target node for pathfinding, dependant on task status
            taskStatusMapping = {
                "retrieving": self.currentTask.pickupNode,
                "pickedUp": self.currentTask.dropoffNode,
                "unassigned": self.targetNode,
                None: None,
            }
            # print(self.taskStatus)
            self.targetNode = taskStatusMapping[self.taskStatus]
            return self.targetNode
        else:
            taskStatusMapping = {
                "unassigned": self.targetNode,
                None: None,
            }
            return self.targetNode

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
    
    def executeMove(self, targetNode):
        """
            Move the agent to the targetNode, to be done only after the move is valid
        """
        logging.debug(f"Moving agent '{self.ID}' to node '{targetNode}'")
        # print(f"Moving agent '{self.ID}' to node '{targetNode}'")
        # self.mainViewRef.simCanvas.requestRender("agent", "move", {"agentNumID": self.numID, "sourceNodeID": self.currentNode, "targetNodeID": targetNode})
        # self.mainViewRef.simCanvas.handleRenderQueue()
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
        self.parent.parent.parent.simulationWindow.simDataView.updateAgentTreeView()