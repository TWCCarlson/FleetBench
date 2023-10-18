import pprint
import logging
import time
import random
from pathfindScripts.aStar import aStarPathfinder
from pathfindScripts.LRAstarPathfinder import LRAstarPathfinder
from pathfindScripts.CAstarPathfinder import CAstarPathfinder
from pathfindScripts.HCAstarPathfinder import HCAstarPathfinder
from pathfindScripts.WHCAstarPathfinder import WHCAstarPathfinder
from pathfindMoverScripts.LRAstarMover import LRAstarMover
from pathfindManagerScripts.CAstarReserver import CAstarReserver
from pathfindManagerScripts.HCAstarReserver import HCAstarReserver
from pathfindManagerScripts.WHCAstarReserver import WHCAstarReserver
from pathfindMoverScripts.CAstarMover import CAstarMover
from pathfindMoverScripts.HCAstarMover import HCAstarMover
from pathfindMoverScripts.WHCAstarMover import WHCAstarMover
from pathfindMoverScripts.defaultMover import defaultAgentMover
pp = pprint.PrettyPrinter(indent=4)
from copy import deepcopy

class simProcessor:
    def __init__(self, parent, simulationSettings):
        self.parent = parent
        self.simulationSettings = simulationSettings

        # Map states to actions
        self.simulationStateMachineMap = {
            "newSimStep": {
                "exec": self.newSimStep,
                "stateLabel": "Preparing Next Step",
                "renderStateBool": simulationSettings["renderNewSimStep"],
                "stateRenderDuration": simulationSettings["renderNewSimStepTime"]
            },
            "selectAgent": {
                "exec": self.selectAgent,
                "stateLabel": "Selecting Next Agent",
                "renderStateBool": simulationSettings["renderAgentSelect"],
                "stateRenderDuration": simulationSettings["renderAgentSelectTime"]
            },
            "taskAssignment": {
                "exec": self.taskAssignment,
                "stateLabel": "Assigning Available Tasks",
                "renderStateBool": simulationSettings["renderTaskAssignment"],
                "stateRenderDuration": simulationSettings["renderTaskAssignmentTime"]
            },
            "selectAction": {
                "exec": self.selectAction,
                "stateLabel": "Evaluating Actions",
                "renderStateBool": simulationSettings["renderAgentActionSelection"],
                "stateRenderDuration": simulationSettings["renderAgentActionSelectionTime"]
            },
            "taskInteraction": {
                "exec": self.taskInteraction,
                "stateLabel": "Task Interaction",
                "renderStateBool": simulationSettings["renderTaskInteraction"],
                "stateRenderDuration": simulationSettings["renderTaskInteractionTime"]
            },
            "agentPlanMove": {
                "exec": self.agentPlanMove,
                "stateLabel": "Agent Planning Move",
                "renderStateBool": simulationSettings["renderAgentPlanMove"],
                "stateRenderDuration": simulationSettings["renderAgentPlanMoveTime"]
            },
            "agentMove": {
                "exec": self.agentMove,
                "stateLabel": "Agent Moving",
                "renderStateBool": simulationSettings["renderAgentMovement"],
                "stateRenderDuration": simulationSettings["renderAgentMovementTime"]
            },
            "agentPathfind": {
                "exec": self.agentPathfind,
                "stateLabel": "Agent Finding Path",
                "renderStateBool": simulationSettings["renderAgentPathfind"],
                "stateRenderDuration": simulationSettings["renderAgentPathfindTime"]
            },
            "checkAgentQueue": {
                "exec": self.checkAgentQueue,
                "stateLabel": "Checking Agent Queue",
                "renderStateBool": simulationSettings["renderCheckAgentQueue"],
                "stateRenderDuration": simulationSettings["renderCheckAgentQueueTime"]
            },
            "simulationErrorState": {
                "exec": self.simulationError,
                "stateLabel": "Simulation Encountered Error",
                "renderStateBool": True,
                "stateRenderDuration": 1
            },
            "endSimStep": {
                "exec": self.endSimStep,
                "stateLabel": "Ending Simulation Step",
                "renderStateBool": simulationSettings["renderEndSimStep"],
                "stateRenderDuration": simulationSettings["renderEndSimStepTime"]
            },
            "endSimulation": {
                "exec": self.endSimulation,
                "stateLabel": "Simulation Complete",
                "renderStateBool": True,
                "stateRenderDuration": 1
            }
        }

        # Default values
        self.simulationStepCount = 0
        self.simulationStateID = "newSimStep"
        self.requestedStateID = None
        self.agentGenerator = None
        self.doNextStep = True
        self.SIMULATION_STATE_SAVE_INCREMENT = 1

        # Acquire state information references
        self.simGraphDataRef = self.parent.simGraphData
        self.simGraph = self.parent.simGraphData.simMapGraph
        self.simAgentManagerRef = self.parent.simAgentManager
        self.simTaskManagerRef = self.parent.simTaskManager
        self.simConfigRef = self.parent.parent.parent.simulationConfigWindow
        self.simCanvasRef = self.parent.parent.simulationWindow.simMainView.simCanvas

        # Acquire algorithm setting
        self.algorithmSelection, self.algorithmType = self.getSelectedSimulationAlgorithm()

        # Map options to pathfinders
        algorithmDict = {
            "Single-agent A*": (aStarPathfinder, None, None),
            "Multi-Agent A* (LRA*)": (LRAstarPathfinder, None, LRAstarMover),
            "Multi-Agent Cooperative A* (CA*)": (CAstarPathfinder, CAstarReserver, CAstarMover),
            "Hierarchical A* with RRA* (HCA*)": (HCAstarPathfinder, HCAstarReserver, HCAstarMover),
            "Windowed HCA* (WHCA*)": (WHCAstarPathfinder, WHCAstarReserver, WHCAstarMover)
        }
        algorithmConfigDict = {
            "Single-agent A*": {"heuristic": simulationSettings["aStarPathfinderConfig"]["algorithmSAPFAStarHeuristic"],
                                "heuristicCoefficient": simulationSettings["aStarPathfinderConfig"]["algorithmSAPFAStarHeuristicCoefficient"]},
            "Multi-Agent A* (LRA*)": {"heuristic": simulationSettings["LRAstarPathfinderConfig"]["algorithmMAPFLRAstarHeuristic"],
                                      "heuristicCoefficient": simulationSettings["LRAstarPathfinderConfig"]["algorithmMAPFLRAstarHeuristicCoefficient"]},
            "Multi-Agent Cooperative A* (CA*)": {"heuristic": simulationSettings["CAstarPathfinderConfig"]["algorithmMAPFCAstarHeuristic"],
                                                 "heuristicCoefficient": simulationSettings["CAstarPathfinderConfig"]["algorithmMAPFCAstarHeuristicCoefficient"]},
            "Hierarchical A* with RRA* (HCA*)": {"heuristic": simulationSettings["HCAstarPathfinderConfig"]["algorithmMAPFHCAstarHeuristic"],
                                                 "heuristicCoefficient": simulationSettings["HCAstarPathfinderConfig"]["algorithmMAPFHCAstarHeuristicCoefficient"]},
            "Windowed HCA* (WHCA*)": {"heuristic": simulationSettings["WHCAstarPathfinderConfig"]["algorithmMAPFWHCAstarHeuristic"],
                                      "heuristicCoefficient": simulationSettings["WHCAstarPathfinderConfig"]["algorithmMAPFWHCAstarHeuristicCoefficient"],
                                      "windowSize": simulationSettings["WHCAstarPathfinderConfig"]["algorithmMAPFWHCAstarWindowSize"]}
        }

        # Call option's pathfinder class
        self.agentCollisionBehavior = self.simulationSettings["agentCollisionsValue"]
        self.agentActionAlgorithm = algorithmDict[self.algorithmSelection][0]
        self.agentActionConfig = algorithmConfigDict[self.algorithmSelection]
        self.agentActionConfig["agentCollisionsValue"] = self.agentCollisionBehavior

        # Call option's shared information manager
        infoShareManager = algorithmDict[self.algorithmSelection][1]
        if infoShareManager is not None:
            self.infoShareManager = infoShareManager(self.simGraph)
        else:
            self.infoShareManager = None

        # Call option's agent movement manager
        agentMovementManager = algorithmDict[self.algorithmSelection][2]
        if agentMovementManager is not None:
            self.agentMovementManager = agentMovementManager(self.simCanvasRef, self.simGraph, self.infoShareManager, self.simAgentManagerRef, self.simTaskManagerRef, self.simCanvasRef)
        else:
            self.agentMovementManager = defaultAgentMover(self.simCanvasRef, self.simGraph, self.infoShareManager, self.simAgentManagerRef, self.simTaskManagerRef, self.simCanvasRef)

        # State history control
        self.stateHistoryManager = simProcessStateHandler(self)

        # Profiling
        self.stateStartTime = time.perf_counter()
        self.loopStartTime = time.perf_counter()
        self.resetIterablesCounter = 0
        self.taskGenerationCounter = 0
        self.selectAgentCounter = 0
        self.executeAgentActionCounter = 0
        self.renderGraphStateCounter = 0
        self.incrementStepCounterCounter = 0
        self.currentState = "newSimStep"
        self.persistRenders = False
        
    def simulationStopTicking(self):
        self.parent.parent.parent.after_cancel(self.simulationUpdateTimer)

    def setInitialMapState(self):
        if self.infoShareManager is not None:
            self.infoShareManager.build()

        self.agentQueue = list(self.simAgentManagerRef.agentList.keys())
        # pp.pprint(self.simGraph.edges('(1, 0)'))
        # pp.pprint(self.simGraph.nodes())
        # import networkx as nx
        # nx.Graph().edges

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
        # self.stateEndTime = time.perf_counter()
        # print(f"State {self.currentState} lasted: {self.stateEndTime - self.stateStartTime}")
        # self.stateStartTime = time.perf_counter()
        # Track the new current state
        self.currentState = stateID
        
        # Update step display label
        targetLabelText = self.parent.parent.simulationWindow.simStepView.simStatusTextValue
        targetLabelText.set(self.simulationStateMachineMap[stateID]["stateLabel"])

        # Enact the state
        
        # self.stateTimerStart = time.perf_counter()
        self.simulationStateMachineMap[stateID]["exec"]()
        # self.stateTimerEnd = time.perf_counter()
        # print(f"State {self.currentState} function time: {self.stateTimerEnd-self.stateTimerStart}")

        # Trigger the next state machine update
        self.previousStateID = stateID
        nextStateID = self.requestedStateID
        self.requestedStateID = None

        # Save the next state's ID for state machine's memory
        self.simulationStateID = nextStateID

        # Render the state
        if self.simulationStateMachineMap[self.currentState]["renderStateBool"]:
            # Handle the render queue for this step
            self.simCanvasRef.handleRenderQueue()
            if not self.persistRenders:
                self.simCanvasRef.requestRender("highlight", "clear", {})
                self.simCanvasRef.requestRender("canvasLine", "clear", {})
                self.simCanvasRef.requestRender("text", "clear", {})
            self.persistRenders = False
        else:
            self.simCanvasRef.renderQueue = []
            self.simCanvasRef.requestRender("highlight", "clear", {})
            self.simCanvasRef.requestRender("canvasLine", "clear", {})
            self.simCanvasRef.requestRender("text", "clear", {})
            self.simCanvasRef.handleRenderQueue()
            self.persistRenders = False

        # Call the next state
        if self.doNextStep:
            self.simulationStateMachineNextStep(nextStateID)

        
        ### Generate new tasks
        ### Calculate/execute agent moves
            # Charge expenditures
            # Agent states/goals update
        ### Execute task interactions if applicable
        ### Verify task states

    def simulationStateMachineNextStep(self, stateID=None):
        # If a specific state is called for, use it
        if stateID is None:
            # Else, use the stored state value
            stateID = self.simulationStateID

        # Check if the state needs to be rendered
        if self.simulationStateMachineMap[self.currentState]["renderStateBool"]:
            
            # If so, get the render duration
            frameDelay = self.simulationStateMachineMap[self.currentState]["stateRenderDuration"]
            if frameDelay == "":
                # Use the default value
                frameDelay = 300
            # Trigger state machine update after the specified duration
            self.simulationUpdateTimer = self.parent.parent.parent.after(frameDelay, 
                lambda stateID=stateID: self.simulateStep(stateID))
        else:
            # State does not need to be displayed, so call the next state "immediately"
            # Empty the render queue
            self.simCanvasRef.renderQueue = []
            # Use after so that the UI doesn't lock up while doing this
            self.simulationUpdateTimer = self.parent.parent.parent.after(0, 
                lambda stateID=stateID: self.simulateStep(stateID))
            
    def newSimStep(self):
        self.persistRenders = False
        # Profiling
        # self.loopEndTime = time.perf_counter()
        # print(f"Total loop time: {self.loopEndTime - self.loopStartTime}")
        # print("====== NEW LOOP =======")
        # self.loopStartTime = time.perf_counter()
        # Certain objects need to be reset on new steps
        # These objects cause loopbacks in the FSM
        # Prepare for a new step
        # First, save the current state if it is the right time
        targetLabelText = self.parent.parent.simulationWindow.simStepView.simStepCountTextValue
        stepID = targetLabelText.get()
        if stepID % self.SIMULATION_STATE_SAVE_INCREMENT == 0:
            # print(f"Saved simulation state for step {stepID}")
            self.stateHistoryManager.copyCurrentState(stepID)
        # The list of agents needs to be reset for this step
        # print(f"Creating a new list of agents for step {stepID}")

        # Process the agent list, shifting agents who just completed a 
        # self.agentQueue = (agent for agent in self.simAgentManagerRef.agentList.keys())
        self.requestedStateID = "selectAgent"
        return

    def selectAgent(self):
        self.persistRenders = True
        # Select an agent, keeping in mind there may be a queue of agents
        # Building the new agent queue 
        if self.algorithmType == "sapf":
            # Single-agent pathfinding methods
            # Only use the first agent in the list, user error if multiple agents
            self.currentAgent = self.simAgentManagerRef.agentList[0]
            self.agentQueue = []
        elif self.algorithmType == "mapf":
            try:
                # newAgent = next(self.agentQueue)
                # print(f"AGENT QUEUE: {self.agentQueue}")
                newAgent = self.agentQueue.pop(0)
                # print(f"AGENT QUEUE AFTER POP: {self.agentQueue}")
                self.currentAgent = self.simAgentManagerRef.agentList[newAgent]
            except StopIteration:
                # The queue is empty, so the simulation step can end
                # print(f"Reached the end of the agent queue. Next sim step should start.")
                self.requestedStateID = "agentCollisionCheck"
                return
        # There was an agent in the queue, so it should act
        # print(f"New agent {self.currentAgent.ID} has been selected.")
        self.currentAgentActionTaken = False
        self.simCanvasRef.requestRender("highlight", "new", {"targetNodeID": self.currentAgent.position,
                "highlightType": "agentHighlight", "multi": False, "highlightTags": ["agent"+str(self.currentAgent.numID)+"Highlight"]})
        self.requestedStateID = "taskAssignment"
        return

    def taskAssignment(self):
        self.persistRenders = True
        # Assign tasks if agent needs a task
        # Assign a new task if the task status is "unassigned"
        # Or generate a new task if there are not, and generation on demand is enabled
        # Or if there are no tasks, and generation is disabled end the agent's turn
        # print(f"{self.currentAgent.ID}: {self.currentAgent.taskStatus}")
        if self.currentAgent.taskStatus == "unassigned":
            # Agent needs a task
            # print(f"Agent {self.currentAgent.ID} needs a new task.")
            for taskID, task in self.simTaskManagerRef.taskList.items():
                if task.assignee is None and task.taskStatus == "unassigned":
                    # Task is eligible for assignment
                    # print(f"Task {taskID} will be assigned to agent {self.currentAgent.ID}")
                    self.simTaskManagerRef.assignAgentToTask(taskID, self.currentAgent)
                    taskRef = self.simTaskManagerRef.taskList[taskID]
                    self.simCanvasRef.requestRender("highlight", "new", {"targetNodeID": taskRef.pickupPosition,
                        "highlightType": "pickupHighlight", "multi": False, "highlightTags": ["task"+str(taskRef.numID)+"Highlight"]})
                    self.simCanvasRef.requestRender("highlight", "new", {"targetNodeID": taskRef.dropoffPosition,
                        "highlightType": "depositHighlight", "multi": False, "highlightTags": ["task"+str(taskRef.numID)+"Highlight"]})
                    self.requestedStateID = "selectAction"
                    return
            # If there are no tasks meeting the criterion, check if a task can be generated
            if self.simulationSettings["taskGenerationFrequencyMethod"]:
                # print(f"Need to generate new task for agent {self.currentAgent}")
                self.generateTask()
                self.requestedStateID = "taskAssignment"
                return
            else:
                # If task cannot be generated yet, then the agent is free and directionless and does nothing
                # print(f"No available tasks and could not generate a new task for agent {self.currentAgent.ID}, skipping.")
                self.requestedStateID = "selectAgent"
                return
        else:
            # Agent does not need a task, so continue to the next state
            # print(f"Agent {self.currentAgent.ID} has task; continuing to action determination state.")
            self.requestedStateID = "selectAction"
            return

    def selectAction(self):
        self.persistRenders = True
        # Agent needs to determine its action for this step
        # If the agent has already acted, then its "turn" is over
        if self.currentAgentActionTaken == True:
            self.requestedStateID = "selectAgent"
            return

        # If the agent is already on its task-given target tile, it should act immediately
        if self.currentAgent.currentNode == self.currentAgent.returnTargetNode():
            # print(f"Agent {self.currentAgent.ID} is in position to interact with task {self.currentAgent.currentTask.name}")
            # An action is about to be taken, but it could be free
            self.requestedStateID = "taskInteraction"
            if self.simulationSettings["agentMiscOptionTaskInteractCostValue"] == "No cost for pickup/dropoff":
                # print(f"\tInteraction was free.")
                self.currentAgentActionTaken = False
                self.requestedStateID = "taskInteraction"
            elif self.simulationSettings["agentMiscOptionTaskInteractCostValue"] == "Pickup/dropoff require step":
                # print(f"\tInteraction consumed agent's action.")
                self.currentAgentActionTaken = True
                self.requestedStateID = "taskInteraction"
            return
        else:
            # If the agent is not at its target tile, it should be trying to move there
            # print(f"Agent {self.currentAgent.ID} needs to move toward its target tile.")
            self.requestedStateID = "agentPlanMove"
            return
        
    def taskInteraction(self):
        self.persistRenders = False
        # Agent should be able to interact with the task
        # print(f"Agent {self.currentAgent.ID} interacting at {self.currentAgent.currentNode}")
        self.currentAgent.taskInteraction(self.currentAgent.currentNode)

        # If this counted as an action, then the agent cannot move
        if self.currentAgentActionTaken == True:
            # print(f"Agent {self.currentAgent.ID} has no more actions available")
            self.requestedStateID = "checkAgentQueue"
        elif self.currentAgentActionTaken == False and self.currentAgent.currentTask is None:
            # If not, then it can also move
            # print(f"Agent {self.currentAgent.ID} is able to move.")
            self.requestedStateID = "taskAssignment"
        elif self.currentAgentActionTaken == False and self.currentAgent.currentTask is not None:
            self.requestedStateID = "selectAction"
        return

    def agentPlanMove(self):
        self.persistRenders = True
        # Determine whether the agent can move or needs to find a path first
        # The agent needs to move toward its target, ensure it has a pathfinder
        agentTargetNode = self.currentAgent.returnTargetNode()
        if self.currentAgent.pathfinder is None or len(self.currentAgent.pathfinder.plannedPath) == 1 or self.currentAgent.pathfinder.invalid == True:
            # print(f"Agent {self.currentAgent.ID} needs a new pathfinder from {self.currentAgent.currentNode}->{agentTargetNode}")
            self.currentAgent.pathfinder = self.agentActionAlgorithm(self.currentAgent.numID, self.simCanvasRef, self.simGraph, self.currentAgent.currentNode, agentTargetNode, self.agentActionConfig, self.infoShareManager)
        
        # If the agent has a planned path, then it can move along it
        if self.currentAgent.pathfinder.plannedPath:
            # print(f"Agent {self.currentAgent.ID} has a plan: {self.currentAgent.pathfinder.plannedPath}")
            self.simCanvasRef.requestRender("canvasLine", "new", {"nodePath": [self.currentAgent.currentNode] + self.currentAgent.pathfinder.plannedPath[1:], 
                    "lineType": "pathfind"})
            nextNodeInPath = self.currentAgent.pathfinder.plannedPath.pop(1)
            validMove = self.agentMovementManager.submitAgentAction(self.currentAgent, (self.currentAgent.currentNode, nextNodeInPath))
            if validMove is True or validMove is None:
                self.requestedStateID = "checkAgentQueue"
            else:
                print("action invalid")
                self.requestedStateID = "agentPlanMove"
            return
        else:
            # If the agent does not have a complete path, it needs to find one
            # print(f"Agent {self.currentAgent.ID} needs to find a path from {self.currentAgent.currentNode}->{agentTargetNode}")
            self.requestedStateID = "agentPathfind"
            return
         
    def agentMove(self):
        self.persistRenders = False
        # Asks the movement manager to verify there are no collisions on this step of the simulation
        if self.agentCollisionBehavior == "Respected":
            conflicts = self.agentMovementManager.checkAgentCollisions()
            print(f"Conflicts: {conflicts}")
            if conflicts is not None:
                self.agentQueue = conflicts[1]
                self.requestedStateID = "selectAgent"
                return
        self.requestedStateID = "endSimStep"
            
    def agentPathfind(self):
        self.persistRenders = True
        # For speed, only use the rendered version of the pathfinder if the frame is being rendered
        # print(f"Agent {self.currentAgent.ID} searching for path...")
        if self.simulationStateMachineMap["agentPathfind"]["renderStateBool"]:
            pathStatus = self.currentAgent.pathfinder.searchStepRender()
        else:
            pathStatus = self.currentAgent.pathfinder.searchStep()

        if pathStatus == False:
            # print(f"\t...did not finish on this iteration.")
            self.requestedStateID = "agentPathfind"
            return
        elif pathStatus == True:
            # print(f"\t...path was found.")
            # self.simCanvasRef.requestRender("canvasLine", "clear", {})
            # self.simCanvasRef.requestRender("highlight", "clear", {})
            # self.simCanvasRef.requestRender("text", "clear", {})
            # self.simCanvasRef.handleRenderQueue()
            self.requestedStateID = "agentPlanMove"
            return
        elif pathStatus == "wait":
            # print(f"\t...Agent could not find path due to obstructions, wait for cleared path.")
            # self.simCanvasRef.requestRender("highlight", "clear", {})
            # self.simCanvasRef.requestRender("text", "clear", {})
            self.agentMovementManager.submitAgentAction(self.currentAgent, "crash")
            self.currentAgent.pathfinder.__reset__()
            self.requestedStateID = "checkAgentQueue"
            # print(f"!!! {self.agentQueue}")

    def checkAgentQueue(self):
        self.persistRenders = False
        # Check the current queue
        if not self.agentQueue:
            # If the queue is empty, then movements can resolve
            self.requestedStateID = "agentMove"
            return
        else:
            # Otherwise, pull a new agent out of it to take actions
            self.requestedStateID = "selectAgent"
            return

    def simulationError(self):
        # print(f"Simulation reached an error.")
        raise Exception("Simulation reached an error state")
    
    def endSimStep(self):
        self.persistRenders = False
        # print(f"All agents have acted.")
        # print(f"AGENT QUEUE: {self.agentQueue}")
        # if the simulation hasnt reached its "objective", do another step
        self.requestedStateID = "newSimStep"
        targetLabelText = self.parent.parent.simulationWindow.simStepView.simStepCountTextValue
        self.stepCompleted = targetLabelText.get()
        # print(f">>>>>Steps completed: {self.stepCompleted}")
        targetLabelText.set(self.stepCompleted + 1)
        # print(stepCompleted)
        if self.infoShareManager is not None:
            print(self.stepCompleted+1)
            self.infoShareManager.updateSimulationDepth(self.stepCompleted+1)

        self.agentQueue = self.agentMovementManager.getCurrentPriorityOrder()
        self.agentMovementManager.setCurrentPriorityOrder([])
        # print(f"New agent queue: {self.agentQueue}")

    def endSimulation(self):
        print(f"Simulation reached its end goal state.")

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

    def getSelectedSimulationAlgorithm(self):
        logging.info(f"Advancing the simulation step to: {self.simulationStepCount+1}.")
        # Check what the currently in use algorithm is
        algorithmSelection = self.simulationSettings["algorithmSelection"]
        algorithmType = self.simulationSettings["algorithmType"]
        logging.debug(f"Next step started with algorithm: {algorithmSelection}")
        return algorithmSelection, algorithmType
    
class simProcessStateHandler:
    """
        Used to store information about the state of the simulation data for playback
        - Delta table stores information about actions execute on each "step"
        - Snapshots taken at intervals allow for restoration of the state instead of "undoing" each action

        The simulator should be deterministic, so reconstruction from a saved point should always lead to the same state
    """
    def __init__(self, parent):
        self.parent = parent

        self.saveStateList =  {}

    def copyCurrentState(self, stepID):
        # print(f"Triggered save before step {stepID}")
        # Make a new entry in the state table
        self.saveStateList[stepID] = {}
        # Get the agent data
        agentData = self.parent.simAgentManagerRef.packageAgentData()
        self.saveStateList[stepID]["agentData"] = agentData
        # pp.pprint(self.saveStateList[stepID]["agentData"])
        taskData = self.parent.simTaskManagerRef.packageTaskData()
        self.saveStateList[stepID]["taskData"] = taskData
        # pp.pprint(self.saveStateList[stepID]["taskData"])
        self.savedStateIDList = list(self.saveStateList.keys())
        self.parent.parent.parent.simulationWindow.simControlPanel.updateStateSelectionChoices(self.savedStateIDList)

    def loadSavedState(self, stateID):
        # print(f"attempt to load state '{stateID}' from {list(self.saveStateList.keys())}")
        if stateID in self.saveStateList:
            stateData = self.saveStateList[stateID]
            self.parent.simCanvasRef.requestRender("agent", "clear", {})
            self.parent.simCanvasRef.requestRender("highlight", "clear", {})
            self.parent.simCanvasRef.requestRender("canvasLine", "clear", {})
            self.parent.simCanvasRef.requestRender("text", "clear", {})
            self.parent.simCanvasRef.handleRenderQueue()
            targetLabelText = self.parent.parent.parent.simulationWindow.simStepView.simStepCountTextValue
            targetLabelText.set(stateID)    
            self.parent.simAgentManagerRef.loadSavedSimState(stateData["agentData"])
            self.parent.simTaskManagerRef.loadSavedSimState(stateData["taskData"])
            self.parent.simCanvasRef.renderAgents()

            # After loading, reset the statemachine's state to be the start of a step
            self.parent.simulationStateID = "newSimStep"

    def findNearestPreviousState(self, currentStep):
        savedStateIDList = list(self.saveStateList.keys())
        savedStateIDList.reverse()

        for stateID in savedStateIDList:
            # print(f"Current step ({currentStep}) is closest to previous saved step ({stateID})?")
            if currentStep-stateID in range(1, 51):
                return stateID
            
    def findNearestFutureState(self, currentStep):
        savedStateIDList = list(self.saveStateList.keys())
        savedStateIDList.reverse()

        for stateID in savedStateIDList:
            print(f"Current step ({currentStep}) is closest to future saved step ({stateID})?")
            if stateID - currentStep in range(1, 51):
                return stateID
        
        