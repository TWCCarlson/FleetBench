import logging
import copy
import pprint
pp = pprint.PrettyPrinter(indent=4)

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
            else:
                currentTask = None
            self.createNewAgent(
                ID=ID, 
                position=position, 
                orientation=orientation, 
                className=className,
                currentTask=currentTask
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
        self.orientation = kwargs.get("orientation")
        self.className = kwargs.get("className")
        self.currentTask = kwargs.get("currentTask")

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

    def validateCandidateMove(self, targetNode):
        """
            Used to check whether an agent can move to a target node
            - There must be an edge between current node and target node
            - There cannot be an agent in the target node, if the config specifies no agent overlap
        """
        currentNode = f"({self.position[0]}, {self.position[1]})"
        targetNode = f"({targetNode[0]}, {targetNode[1]})"
        logging.debug(f"Checking if currentNode '{currentNode}' and targetNode '{targetNode}' share an edge . . .")
        if not self.mapGraphRef.has_edge(currentNode, targetNode):
            logging.debug("Edge does not exist.")
            return False
        logging.debug("Edge exists.")

        logging.debug(f"Checking if targetNode '{targetNode}' is occupied by an agent . . .")
        if 'agent' in self.mapGraphRef.nodes(data=True)[targetNode]:
            print("teehee")
            logging.debug(f"TargetNode '{targetNode}' contains an agent. Cannot move here.")
            return False
        logging.debug("Node has space to be moved into.")
        
        return True
    
    def executeMove(self, targetNode):
        """
            Move the agent to the targetNode, to be done only after the move is valid
        """
        logging.debug(f"Moving agent '{self.ID}' to node '{targetNode}'")
        self.position = targetNode # Set it as a tuple

        # Update the mapgraph with the new location
        self.parent.parent.simGraphData.updateAgentLocations(self.parent.agentList)