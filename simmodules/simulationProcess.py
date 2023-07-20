from simmodules.simulationMapData import simGraphManager
from simmodules.simulationAgentManager import simAgentManager
from simmodules.simulationTaskManager import simTaskManager
import logging

class simulationProcess():
    # Process used for running the simulation, exposes data to the window for rendering display
    def __init__(self, parent):
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