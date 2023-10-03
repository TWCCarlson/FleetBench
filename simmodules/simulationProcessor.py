import pprint
pp = pprint.PrettyPrinter(indent=4)
import logging
import tkinter as tk
import time
import random
from pathfindScripts.aStar import aStarPathfinder

class simProcessor:
    def __init__(self, parent, simulationSettings):
        self.parent = parent
        self.simulationSettings = simulationSettings

        # Map states to actions
        self.simulationStateMachineMap = {
            "start": {
                "nextState": "resetIterables",
                "exec": None,
                "stateLabel": "Preparing . . .",
                "renderStateBool": False,
                "stateRenderDuration": 0
            },
            "resetIterables": {
                "nextState": "taskGeneration",
                "exec": self.resetIterables,
                "stateLabel": "Preparing Next Step",
                "renderStateBool": simulationSettings["renderResetIterablesStep"],
                "stateRenderDuration": simulationSettings["durationResetIterablesStep"]
            },
            "taskGeneration": {
                "nextState": "selectAgent",
                "exec": self.taskGeneration,
                "stateLabel": "Generating Tasks",
                "renderStateBool": simulationSettings["renderTaskGenerationStep"],
                "stateRenderDuration": simulationSettings["durationTaskGenerationStep"]
            },
            "selectAgent": {
                "nextState": "agentAction",
                "exec": self.selectAgent,
                "stateLabel": "Selecting Next Agent",
                "renderStateBool": simulationSettings["renderAgentSelectionStep"],
                "stateRenderDuration": simulationSettings["durationAgentSelectionStep"]
            },
            "agentAction": {
                "nextState": "renderState",
                "exec": self.executeAgentAction,
                "stateLabel": "Agent Acting",
                "renderStateBool": simulationSettings["renderAgentActionStep"],
                "stateRenderDuration": simulationSettings["durationAgentActionStep"]
            },
            "agentPathfind": {
                "nextState": "renderState",
                "exec": self.agentPathfind,
                "stateLabel": "Agent Seeking Path",
                "renderStateBool": simulationSettings["renderAgentPathfindStep"],
                "stateRenderDuration": simulationSettings["durationAgentPathfindStep"]
            },
            "renderState": {
                "nextState": "incrementStepCounter",
                "exec": self.renderGraphState,
                "stateLabel": "Updating Canvas View",
                "renderStateBool": simulationSettings["renderGraphUpdateStep"],
                "stateRenderDuration": simulationSettings["durationGraphUpdateStep"]
            },
            "incrementStepCounter": {
                "nextState": "resetIterables",
                "exec": self.incrementStepCounter,
                "stateLabel": "Finish Current Step",
                "renderStateBool": simulationSettings["renderSimStepCounterUpdate"],
                "stateRenderDuration": simulationSettings["durationSimStepCounterUpdate"]
            }
        }

        # Default values
        self.simulationStepCount = 0
        self.simulationStateID = "resetIterables"
        self.requestedStateID = None
        self.agentGenerator = None

        # Acquire state information references
        self.simGraphDataRef = self.parent.simGraphData
        self.simGraph = self.parent.simGraphData.simMapGraph
        self.simAgentManagerRef = self.parent.simAgentManager
        self.simTaskManagerRef = self.parent.simTaskManager
        self.simConfigRef = self.parent.parent.parent.simulationConfigWindow
        self.simCanvasRef = self.parent.parent.simulationWindow.simMainView.simCanvas

        # Acquire algorithm setting
        self.algorithmSelection, self.algorithmType = self.getSelectedSimulationAlgorithm()

        # Map options to functions
        algorithmDict = {
            "Single-agent A*": aStarPathfinder
        }

        # Call option's pathfinder class
        self.agentActionAlgorithm = algorithmDict[self.algorithmSelection]

        # Profiling
        self.stateStartTime = time.perf_counter()
        self.loopStartTime = time.perf_counter()
        self.resetIterablesCounter = 0
        self.taskGenerationCounter = 0
        self.selectAgentCounter = 0
        self.executeAgentActionCounter = 0
        self.renderGraphStateCounter = 0
        self.incrementStepCounterCounter = 0
        self.currentState = None

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
        # Profiling
        self.stateEndTime = time.perf_counter()
        print(f"State {self.currentState} lasted: {self.stateEndTime - self.stateStartTime}")
        self.stateStartTime = time.perf_counter()
        self.currentState = stateID

        # Update step display label
        targetLabelText = self.parent.parent.simulationWindow.simStepView.simStepTextValue
        targetLabelText.set(self.simulationStateMachineMap[stateID]["stateLabel"])

        # Take actions
        self.simulationStateMachineMap[stateID]["exec"]()

        # Trigger the next state machine update
        self.previousStateID = stateID
        if self.requestedStateID == None:
            nextStateID = self.simulationStateMachineMap[stateID]["nextState"]
        else:
            nextStateID = self.requestedStateID
            self.requestedStateID = None

        # Save the next state's ID for state machine's memory
        self.simulationStateID = nextStateID

        # Call the next state
        
        self.simulationStateMachineNextStep(nextStateID)
        

        ### Generate new tasks
        ### Calculate/execute agent moves
            # Charge expenditures
            # Agent states/goals update
        ### Execute task interactions if applicable
        ### Verify task states

    def simulationStateMachineNextStep(self, stateID=None):
        # If a specific state is called for, use it
        if stateID == None:
            # Else, use the stored state value
            stateID = self.simulationStateID

        # print(f"Render frame: {self.simulationStateMachineMap[stateID]["renderStateBool"]}")
        # Check if the state needs to be rendered
        if self.simulationStateMachineMap[stateID]["renderStateBool"]:
            # If so, get the render duration
            frameDelay = self.simulationStateMachineMap[stateID]["stateRenderDuration"]
            if frameDelay == "":
                # Use the default value
                frameDelay = 300
            # Trigger state machine update after the specified duration
            self.simulationUpdateTimer = self.parent.parent.parent.after(frameDelay, 
                lambda stateID=stateID: self.simulateStep(stateID))
        else:
            # State does not need to be displayed, so call it "immediately"
            # Use after so that the UI doesn't lock up while doing this
            self.simulationUpdateTimer = self.parent.parent.parent.after(1, 
                lambda stateID=stateID: self.simulateStep(stateID))

    def resetIterables(self):
        # self.resetIterablesCounter = self.resetIterablesCounter + 1
        # print(f"     Call count: {self.resetIterablesCounter}")
        # Certain objects need to be reset on new steps
        # These objects cause loopbacks in the FSM

        # Profiling
        self.loopEndTime = time.perf_counter()
        print("====== NEW LOOP =======")
        print(f"Total loop time: {self.loopEndTime - self.loopStartTime}")
        self.loopStartTime = time.perf_counter()


        # Looping over every agent
        self.agentGenerator = (agent for agent in self.simAgentManagerRef.agentList)

    def taskGeneration(self):
        # self.taskGenerationCounter = self.taskGenerationCounter + 1
        # print(f"     Call count: {self.taskGenerationCounter}")
        generationStyle = self.simulationSettings["taskGenerationFrequencyMethod"]
        
        if generationStyle == "As Available":
            # Check if there are agents needing work
            for agentID, agent in self.simAgentManagerRef.agentList.items():
                if agent.taskStatus == self.simulationSettings["taskGenerationAsAvailableTrigger"]:
                    # If agents share the triggering status, create a task and assign it
                    newTaskID = self.generateTask()
                    
                    # Assign the task to the agent, and the agent to the task
                    self.simTaskManagerRef.assignAgentToTask(newTaskID, agent)

                    # Highlight the task during the wait period
                    self.simTaskManagerRef.taskList[newTaskID].highlightTask(multi=False)

                if self.algorithmType == "sapf":
                    # Only do this for one agent
                    break
                elif self.algorithmType == "mapf":
                    # Do this for all agents
                    continue
        elif generationStyle == "Fixed Rate":
            # Unimplemented
            pass

        self.simCanvasRef.requestRender("highlight", "clear", {})

    def generateTask(self):
        # Kwargs for generating a task
        # Packaged taskData: {'name': 'task1', 'pickupPosition': (0, 1), 'dropoffPosition': (4, 8), 'timeLimit': 0, 'assignee': 0}
        # name is optional, no need to generate one
        pickupNodes = self.simulationSettings["taskNodeAvailableDict"]["pickup"]
        dropoffNodes = self.simulationSettings["taskNodeAvailableDict"]["dropoff"]
        
        pickupNode = random.choice(list(pickupNodes.keys()))
        dropoffNode = random.choice(list(dropoffNodes.keys()))
        timeLimit = 0
        assignee = None
        taskStatus = "unassigned"

        newTaskID = self.simTaskManagerRef.createNewTask(pickupNode=pickupNode, dropoffNode=dropoffNode,
                        timeLimit=timeLimit, assignee=assignee, taskStatus=taskStatus)

        return newTaskID

    def renderGraphState(self):
        # self.renderGraphStateCounter = self.renderGraphStateCounter + 1
        # print(f"     Call count: {self.renderGraphStateCounter}")
        self.parent.parent.simulationWindow.simMainView.simCanvas.handleRenderQueue()
        print(f"Objects in canvas: {len(self.parent.parent.simulationWindow.simMainView.simCanvas.find_all())}")

    def incrementStepCounter(self):
        # self.incrementStepCounterCounter = self.incrementStepCounterCounter + 1
        # print(f"     Call count: {self.incrementStepCounterCounter}")
        pass

    def selectAgent(self):
        # self.selectAgentCounter = self.selectAgentCounter + 1
        # print(f"     Call count: {self.selectAgentCounter}")
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
        
    def executeAgentAction(self):
        # If the agent has a task, move it toward completing the task
        if self.currentAgent.currentTask == None:
            # If not, do nothing
            return
        # If so, identify the target node
        agentTargetNode = self.currentAgent.returnTargetNode()

        # If the agent is at its target node
        if self.currentAgent.currentNode == agentTargetNode:
            self.currentAgent.pathfinder = None
            self.currentAgent.taskInteraction(agentTargetNode)
            if self.simulationSettings["agentMiscOptionTaskInteractCostValue"] == "Pickup/dropoff require step":
                return
            elif self.simulationSettings["agentMiscOptionTaskInteractCostValue"] == "No cost for pickup/dropoff":
                # Calculate a new target before continuing to move
                agentTargetNode = self.currentAgent.returnTargetNode()

        # If the agent needs to move toward its target, ensure it has a pathfinder
        if self.currentAgent.pathfinder is None:
            self.currentAgent.pathfinder = self.agentActionAlgorithm(self.simCanvasRef, self.simGraph, self.currentAgent.currentNode, agentTargetNode)

        # If a path has already been planned, follow it
        if self.currentAgent.pathfinder.plannedPath:
            nextNodeInPath = self.currentAgent.pathfinder.plannedPath.pop(1)
            if self.currentAgent.validateCandidateMove(nextNodeInPath):
                # If the node is a valid, unobstructed move, move there
                self.currentAgent.executeMove(nextNodeInPath)
                # If, after moving, the target is interactable, do so
                if self.currentAgent.currentNode == agentTargetNode and self.simulationSettings["agentMiscOptionTaskInteractCostValue"] == "No cost for pickup/dropoff":
                    self.currentAgent.taskInteraction(agentTargetNode)
                    self.currentAgent.pathfinder = None
            else:
                # Node is blocked, have to replan
                self.currentAgent.pathfinder = self.agentActionAlgorithm(self.simCanvasRef, self.simGraph, self.currentAgent.currentNode, agentTargetNode)
                self.requestedStateID = "agentPathfind"
        else:
            # Otherwise, keep searching
            self.requestedStateID = "agentPathfind"

    def agentPathfind(self):
        self.simCanvasRef.requestRender("canvasLine", "clear", {})
        self.simCanvasRef.handleRenderQueue()

        self.currentAgent.pathfinder.searchStepRender()

        if not self.currentAgent.pathfinder.plannedPath:
            self.requestedStateID = "agentPathfind"
        else:
            self.requestedStateID = "agentAction"

    def getSelectedSimulationAlgorithm(self):
        logging.info(f"Advancing the simulation step to: {self.simulationStepCount+1}.")
        # Check what the currently in use algorithm is
        algorithmSelection = self.simulationSettings["algorithmSelection"]
        algorithmType = self.simulationSettings["algorithmType"]
        logging.debug(f"Next step started with algorithm: {algorithmSelection}")
        return algorithmSelection, algorithmType

    def algorithmSingleAgentAStar(self):
        """
            A* implementation for a single agent, does not work with multi-agent
            Set up to use the first agent in the agent list, so that other agents can act as blockers
            Useful as a way to find the shortest current path
        """
        pass
        