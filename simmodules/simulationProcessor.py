import pprint
pp = pprint.PrettyPrinter(indent=4)
import logging

class simProcessor:
    def __init__(self, parent, simulationSettings):
        self.parent = parent
        self.simulationSettings = simulationSettings

        # Default values
        self.simulationStepCount = 0

        # self.simulateStep()
        # self.simulationUpdateTimer = self.parent.parent.parent.after(1000, self.simulationUpdateTick)
        # print(self.simulationUpdateTimer)

    def simulationUpdateTick(self):
        frameDelay = self.simulationSettings['playbackFrameDelay']
        if frameDelay == "":
            # Use the default value
            frameDelay = 1000
            
        logging.debug(f"User triggered simulationUpdateTick with rate: {frameDelay}ms")
        self.simulateStep()
        self.simulationUpdateTimer = self.parent.parent.parent.after(frameDelay, self.simulationUpdateTick)
        print(self.simulationUpdateTimer)

    def simulationStopTicking(self):
        self.parent.parent.parent.after_cancel(self.simulationUpdateTimer)

    def simulateStep(self):
        """
            Check for selected algorithm
            Feed algorithm all the simulation state information
            - Iterate over agents, top->bottom? bottom->top? some kind of adaptive technique? short distances to go first? long first?
            Collect algorithm Orders
            Validate any interactions
            - Pickup, dropoff, resting, task completion
            Record the history for replay
            Render the new state
            - Update statistics
        """
        algorithmSelection = self.getSelectedSimulationAlgorithm()

        # Acquire state information references
        simGraphData = self.parent.simGraphData
        simAgentManager = self.parent.simAgentManager
        simTaskManager = self.parent.simTaskManager

        # pp.pprint(simGraphData.simMapGraph.nodes(data=True))

        # Execute algorithm for every agent currently in the simulation
        # Alternative ways of iterating through the agent list may be of interest later
        for agent in simAgentManager.agentList:
            logging.debug(f"Algorithm acting on agent: '{agent}:{simAgentManager.agentList[agent].ID}'")
            agentCurrentNode = simAgentManager.agentList[agent].position
            agentCurrentXPos = agentCurrentNode[0]
            agentCurrentYPos = agentCurrentNode[1]
            # print(f"({agentCurrentXPos}, {agentCurrentYPos})")
            # Temporarily just move the agent upward
            agentTargetNode = (agentCurrentXPos, agentCurrentYPos-1)
            # print(agentTargetNode)
            # print(type(agentTargetNode))
            validMove = simAgentManager.agentList[agent].validateCandidateMove(agentTargetNode)
            if validMove:
                simAgentManager.agentList[agent].executeMove(agentTargetNode)
            else:
                logging.error(f"'{agentTargetNode}' is not a valid node for movement.")

        self.parent.parent.simulationWindow.simMainView.simCanvas.renderGraphState()

    def getSelectedSimulationAlgorithm(self):
        logging.info(f"Advancing the simulation step to: {self.simulationStepCount+1}.")
        # Check what the currently in use algorithm is
        algorithmSelection = self.simulationSettings["algorithmSelection"].get()
        logging.debug(f"Next step started with algorithm: {algorithmSelection}")
        return algorithmSelection