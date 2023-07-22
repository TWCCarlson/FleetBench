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
