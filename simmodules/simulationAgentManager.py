import logging
import copy
import pprint
pp = pprint.PrettyPrinter(indent=4)

class simAgentManager:
    def __init__(self, parent):
        self.parent = parent

        # Data structures
        self.agentList = {}

        # Scrape the configured data
        self.retrieveInitialSimState()
        logging.debug("Class 'simAgentManager' initialized.")

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

    def retrieveInitialSimState(self):
        # Extract the data from the session edit window data
        dataPackage = self.parent.parent.parent.agentManager.packageAgentData()
        # Populate the agent condition into the 
        for agent in dataPackage:
            ID = dataPackage[agent]["ID"]
            position = dataPackage[agent]["position"]
            orientation = dataPackage[agent]["orientation"]
            className = dataPackage[agent]["className"]
            self.createNewAgent(
                ID=ID, 
                position=position, 
                orientation=orientation, 
                className=className
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
        self.numID = kwargs.pop("numID")    # Numeric ID, internal use
        self.ID = kwargs.pop("ID")          # Human-readable ID, name
        self.position = kwargs.pop("position")
        self.orientation = kwargs.pop("orientation")
        self.className = kwargs.pop("className")

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
        logging.debug(f"Checking if currentNode '{currentNode}' and '{targetNode}' share an edge . . .")
        edgeExists = self.mapGraphRef.has_edge(currentNode, targetNode)
        logging.debug(f"Edge existence: {edgeExists}")
        return edgeExists
    
    def executeMove(self, targetNode):
        """
            Move the agent to the targetNode, to be done only after the move is valid
        """
        logging.debug(f"Moving agent '{self.ID}' to node '{targetNode}'")
        self.position = targetNode # Set it as a tuple