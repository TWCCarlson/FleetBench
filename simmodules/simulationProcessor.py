import pprint
pp = pprint.PrettyPrinter(indent=4)
import logging
import tkinter as tk
import time

class simProcessor:
    def __init__(self, parent, simulationSettings):
        self.parent = parent
        self.simulationSettings = simulationSettings

        # Map states to actions
        self.simulationStateMachineMap = {
            "start": {
                "nextState": "resetIterables",
                "exec": None
            },
            "resetIterables": {
                "nextState": "taskGeneration",
                "exec": self.resetIterables
            },
            "taskGeneration": {
                "nextState": "selectAgent",
                "exec": self.taskGeneration
            },
            "selectAgent": {
                "nextState": "movementExecute",
                "exec": self.selectAgent
            },
            "movementExecute": {
                "nextState": "renderState",
                "exec": self.moveAgent
            },
            "renderState": {
                "nextState": "incrementStepCounter",
                "exec": self.renderGraphState
            },
            "incrementStepCounter": {
                "nextState": "taskGeneration",
                "exec": self.incrementStepCounter
            }
        }

        # Default values
        self.simulationStepCount = 0
        self.simulationStateID = "resetIterables"
        self.requestedStateID = None
        self.agentGenerator = None

        # Acquire state information references
        self.simGraphDataRef = self.parent.simGraphData
        self.simAgentManagerRef = self.parent.simAgentManager
        self.simTaskManagerRef = self.parent.simTaskManager
        self.simConfigRef = self.parent.parent.parent.simulationConfigWindow

        # Acquire algorithm setting
        self.algorithmSelection, self.algorithmType = self.getSelectedSimulationAlgorithm()

        # Map options to functions
        algorithmDict = {
            "Dummy": self.algorithmDummy,
            "Single-agent A*": self.algorithmSingleAgentAStar
        }

        # Call option's function
        self.agentActionAlgorithm = algorithmDict[self.algorithmSelection]

    def simulationStopTicking(self):
        self.parent.parent.parent.after_cancel(self.simulationUpdateTimer)

    def simulateStep(self, stateID):
        """
            FSM:
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
        
        # Take actions
        self.simulationStateMachineMap[stateID]["exec"]()

        # Trigger the next state machine update
        if self.requestedStateID == None:
            nextStateID = self.simulationStateMachineMap[stateID]["nextState"]
        else:
            nextStateID = self.requestedStateID
            self.requestedStateID = None

        self.simulationStateID = nextStateID
        self.simulationStateMachineNextStep(nextStateID)
        ### Generate new tasks
        ### Calculate/execute agent moves
            # Charge expenditures
            # Agent states/goals update
        ### Execute task interactions if applicable
        ### Verify task states

    def simulationStateMachineNextStep(self, stateID=None):
        # Call the state machine to evaluate the next state
        frameDelay = self.simulationSettings['playbackFrameDelay']
        if frameDelay == "":
            # Use the default value
            frameDelay = 1000

        # If a specific state is called for, use it
        if stateID == None:
            # Else, use the stored state value
            stateID = self.simulationStateID

        # Trigger state machine update
        self.simulationUpdateTimer = self.parent.parent.parent.after(frameDelay, 
            lambda stateID=stateID: self.simulateStep(stateID))

    def resetIterables(self):
        # Certain objects need to be reset on new steps
        # These objects cause loopbacks in the FSM

        # Looping over every agent
        self.agentGenerator = (agent for agent in self.simAgentManagerRef.agentList)

    def taskGeneration(self):
        pass

    def renderGraphState(self):
        self.parent.parent.simulationWindow.simMainView.simCanvas.renderGraphState()

    def incrementStepCounter(self):
        pass

    def selectAgent(self):
        if self.algorithmType == "sapf":
            # Single-agent pathfinding methods
            # Only use the first agent in the list, user error if multiple agents
            self.currentAgent = self.simAgentManagerRef.agentList[0]
        elif self.algorithmType == "mapf":
            # agentGenerator acts as a queue for what agents still need to be moved
            try:
                self.currentAgent = next(self.agentGenerator)
                self.requestedStateID = "selectAgent"
            except StopIteration:
                # No more agents in the queue
                return   
            else:
                logging.error("Algorithm type is not SAPF/MAPF")
                raise Exception("Algorithm type is not SAPF/MAPF")
        
        # Highlight the agent
        self.currentAgent.highlightAgent(multi=False)
        
    def moveAgent(self):
        self.agentActionAlgorithm()
    
    def getSelectedSimulationAlgorithm(self):
        logging.info(f"Advancing the simulation step to: {self.simulationStepCount+1}.")
        # Check what the currently in use algorithm is
        algorithmSelection = self.simulationSettings["algorithmSelection"]
        algorithmType = self.simulationSettings["algorithmType"]
        logging.debug(f"Next step started with algorithm: {algorithmSelection}")
        return algorithmSelection, algorithmType

    def algorithmDummy(self):
        """
            Temporary algorithm that just moves agents directly upward
        """
        # Acquire state information references
        simGraphData = self.parent.simGraphData
        simAgentManager = self.parent.simAgentManager
        simTaskManager = self.parent.simTaskManager

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
                simAgentManager.agentList[agent].highlightAgent(multi=False)
            else:
                logging.error(f"'{agentTargetNode}' is not a valid node for movement.")

    def algorithmSingleAgentAStar(self):
        """
            A* implementation for a single agent, does not work with multi-agent
            Set up to use the first agent in the agent list, so that other agents can act as blockers
            Useful as a way to find the shortest current path
        """
        # If the agent has a task, move it toward completing the task
        if self.currentAgent.currentTask == None:
            # If not, do nothing
            return
        
        agentTargetNode = self.currentAgent.returnTargetNode()
        
        # Take a step toward the task if not already there
        if self.currentAgent.currentNode == agentTargetNode:
            self.currentAgent.taskInteraction(agentTargetNode)
        elif self.currentAgent.currentNode != agentTargetNode:
            # Find the best path length
            bestAStarPathLength = self.currentAgent.calculateAStarBestPath(agentTargetNode)
            # Find the list of best paths sharingf that length
            bestPathsList = self.currentAgent.findAllSimplePathsOfCutoffK(agentTargetNode, bestAStarPathLength)
            # Use the first path in the list for now, and 
            currentNodeListIndex = bestPathsList[0].index(self.currentAgent.currentNode)
            # Fetch the next node to move to
            nextNodeInList = bestPathsList[0][currentNodeListIndex+1]
            if self.currentAgent.validateCandidateMove(nextNodeInList):
                # If it is a valid node, move there
                self.currentAgent.executeMove(nextNodeInList)