from simmodules.simulationMapData import simGraphManager
from simmodules.simulationAgentManager import simAgentManager
from simmodules.simulationTaskManager import simTaskManager
from simmodules.simulationProcessor import simProcessor
import logging

class simulationProcess():
    # Process used for running the simulation, exposes data to the window for rendering display
    def __init__(self, parent, simulationSettings):
        self.parent = parent

        # Build simulation graph data store
        self.simGraphData = simGraphManager(self)
        logging.info("Simulation Info Class 'simGraphManager' instantiated successfully.")

        # Build simulation agent manager
        self.simAgentManager = simAgentManager(self)
        logging.info("Simulation Info Class 'simAgentManager' instantiated successfully.")

        # Build simulation task manager
        self.simTaskManager = simTaskManager(self)
        logging.info("Simulation Info Class 'simTaskManager' instantiated successfully.")

        # Build simulation executor
        self.simProcessor = simProcessor(self, simulationSettings)
        logging.info("Simulation Execution Class 'simProcessor' instantiated successfully.")

        # Build backreferences
        self.simGraphData.buildReferences()
        self.simAgentManager.buildReferences()
        self.simTaskManager.buildReferences()

        # Load in the initial states of the simulation
        self.simGraphData.retrieveInitialSimState()
        self.simAgentManager.retrieveInitialSimState()
        self.simTaskManager.retrieveInitialSimState()

        # Fix any non-object references
        self.simAgentManager.fixAssignments()
        self.simTaskManager.fixAssignments()