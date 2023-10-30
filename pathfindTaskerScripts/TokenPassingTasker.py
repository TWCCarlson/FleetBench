import random
from numpy import inf
from heapq import heappush, heappop
from itertools import count
from copy import deepcopy

class TokenPassingTasker:
    """
        Fallback method for generating and assigning tasks
    """
    def __init__(self, pickupNodes, depositNodes, nodeWeights, validNodes, canvasRef, graphRef, infoShareManager, simAgentManager, simTaskManager, simulationSettings):
        self.pickupNodes = pickupNodes
        self.depositNodes = depositNodes
        self.nodeWeights = nodeWeights
        self.validNodes = validNodes
        self.canvasRef = canvasRef
        self.graphRef = graphRef
        self.infoShareManager = infoShareManager
        self.simAgentManager = simAgentManager
        self.simTaskManager = simTaskManager
        self.simulationSettings = simulationSettings

        self.processNodeList()

    def processNodeList(self):
        pass

    def generateTask(self):
        pickupNode = random.choice(list(self.pickupNodes.keys()))
        depositNode = random.choice(list(self.depositNodes.keys()))
        timeLimit = 0
        assignee = None
        taskStatus = "unassigned"

        newTaskID = self.simTaskManager.createNewTask(pickupNode=pickupNode, 
            dropoffNode=depositNode, timeLimit=timeLimit, assignee=assignee, taskStatus=taskStatus)
        return newTaskID
    
    def AStar(self, sourceNode, targetNode, startTime, agentID, ignoredAgent=None):
        # print(f"{agentID} seeks {sourceNode}->{targetNode} from relative T{startTime}, ignoring {ignoredAgent}")
        # if sourceNode == targetNode:
        #     # Trivial path
        #     path = [sourceNode, targetNode]
        #     return path
        weight = 1
        gScore = {}
        fScore = {}
        cameFrom = {}
        counter = count()
        openSet = []
        # Set the first node
        heappush(openSet, (0, next(counter), sourceNode, startTime))
        gScore[(sourceNode, startTime)] = 0
        fScore[(sourceNode, startTime)] = self.infoShareManager.hScores[targetNode][sourceNode]
        # Begin searching
        while openSet:
            # Get the next best node to explore
            _, __, currentNode, timeDepth = heappop(openSet)
            # print(f"Exploring {currentNode} at T+{timeDepth}")
            # If it is the goal
            if currentNode == targetNode and timeDepth != 0:
                # Reconstruct the path from best parents
                path = [currentNode]
                parentNode = cameFrom.get((currentNode, timeDepth), None)
                while parentNode is not None:
                    path.append(parentNode[0])
                    parentNode = cameFrom.get(parentNode, None)
                # Reverse the path to get source->target
                path.reverse()
                return path
            # If not, examine successors
            neighborNodes = list(self.graphRef.neighbors(currentNode)) + [currentNode]
            for neighborNode in neighborNodes:
                # print(f">>>Evaluate {currentNode}->{neighborNode}>>{targetNode}: {timeDepth}")
                if not self.infoShareManager.evaluateNodeEligibility(timeDepth, neighborNode, currentNode, agentID, ignoredAgent) and self.simulationSettings["agentCollisionsValue"] == "Respected":
                    # print("Not eligible")
                    # Node is blocked, but if its an agent we want to ignore that is fine
                    continue
                if neighborNode == targetNode:
                    if not self.infoShareManager.evaluateEndpointEligibility(timeDepth, neighborNode, agentID, ignoredAgent):
                        # print("Endpoint reserved")
                        # Endpoint is not available to rest in
                        continue
                # Node g scores increase by "weight" per step
                est_gScore = gScore[(currentNode, timeDepth)] + weight
                # If this estimated gScore is an improvement over the existing value (default infinity for unexpanded nodes)
                if est_gScore < gScore.get((neighborNode, timeDepth+1), inf):
                    # Then a new best path to this node has been found
                    cameFrom[(neighborNode, timeDepth+1)] = (currentNode, timeDepth)
                    # Record the new gScore
                    gScore[(neighborNode, timeDepth+1)] = est_gScore
                    # Calculate nodes estimated distance from the goal
                    hScore = self.infoShareManager.hScores[targetNode][neighborNode]
                    # Calculate the fScore for the new node
                    node_fScore = est_gScore + hScore
                    # If the node isn't in the openSet, it should be added
                    if (neighborNode, timeDepth+1) not in fScore:
                        heappush(openSet, (node_fScore, next(counter), neighborNode, timeDepth+1))
                    # Update the node's fScore
                    fScore[(neighborNode, timeDepth+1)] = node_fScore
        return False

    def selectTaskForAgent(self, currentAgent):
        validTasks = []
        claimedEndpoints = []
        # The list of claimed endpoints is equivalent to the POIs for tasks that are not unassigned
        # for taskID, task in self.simTaskManager.taskList.items():
        #     if task.assignee is not None:
        #         if task.taskStatus == "pickedUp":
        #             # No need to treat the tasks start location as reserved
        #             claimedEndpoints.append(task.dropoffNode) # An agent will be here at some point
        #         else:
        #             claimedEndpoints.append(task.pickupNode)
        #             claimedEndpoints.append(task.dropoffNode) # An agent will be here at some point
        # ^ over-reserves
        claimedEndpoints = [path[-1] for agent, path in self.infoShareManager.reservedPaths.items()]
        #  if (not agent == currentAgent.numID)
        # print(f"Finding new task for {currentAgent.numID}")
        # print(f"\tAvoid: \n\t{claimedEndpoints}")
        # ^ This doesn't work when the paths being planned are only to sj, and not fully through gj
        # An agent can reach sj1 of a task 1 that has a gj equal to that of task 2 after an agent reaches sj2
        # The agent reaching sj2 will then claim gj, and then the agent reaching sj1 cannot find a path to gj

        for taskID, task in self.simTaskManager.taskList.items():
            if task.assignee is None and task.taskStatus == "unassigned":
                # Task is eligible for assignment
                # print(f"\tIs task '{taskID}' node sj {task.pickupNode} or gj {task.dropoffNode} in...")
                # print(f"\t...{claimedEndpoints}")
                if task.pickupNode in claimedEndpoints or task.dropoffNode in claimedEndpoints:
                    # Task endpoint is already claimed, so this task is invalid right now
                    # print(">>>yes, not valid")
                    continue
                # Task endpoint is free, so the task is valid for this agent
                # print(">>>no, it is valid")
                validTasks.append(task)
        # If there are no valid tasks, return none
        if len(validTasks) < 1:
            return None

        # For all valid tasks, find their hScores, lowest wins
        winner = inf
        for task in validTasks:
            taskDistance = self.infoShareManager.hScores[task.pickupNode][currentAgent.currentNode]
            if taskDistance < winner:
                winner = taskDistance
                bestTask = task

        # print(f"\tAssigned {bestTask.numID} to {currentAgent.ID}")
        self.simTaskManager.assignAgentToTask(bestTask.numID, currentAgent)
        self.canvasRef.requestRender("highlight", "new", {"targetNodeID": bestTask.pickupPosition,
            "highlightType": "pickupHighlight", "multi": False, "highlightTags": ["task"+str(bestTask.numID)+"Highlight"]})
        self.canvasRef.requestRender("highlight", "new", {"targetNodeID": bestTask.dropoffPosition,
            "highlightType": "depositHighlight", "multi": False, "highlightTags": ["task"+str(bestTask.numID)+"Highlight"]})
        return bestTask.numID
        
    def handleAimlessAgent(self, currentAgent):
        # An agent is aimless if it does not have a target node (no task assigned)
        # In Token Passing, aimless agents need to make sure they are not on top of a task endpoint
        if currentAgent.currentNode not in self.infoShareManager.V_endpoint:
            # print(f"Agent{currentAgent.numID} is not in an endpoint, finding nearest.")
            # Agent is not in an endpoint, needs to move to neareset one
            winner = inf
            # print(self.infoShareManager.V_ntask)
            # Don't use already claimed endpoints
            claimedEndpoints = [path[-1] for agent, path in self.infoShareManager.reservedPaths.items() if (not agent == currentAgent.numID)]
            for endpoint in self.infoShareManager.V_ntask:
                if endpoint in claimedEndpoints:
                    continue
                taskDistance = self.infoShareManager.hScores[endpoint][currentAgent.currentNode]
                if taskDistance < winner:
                    winner = taskDistance
                    bestEndpoint = endpoint
            # This is the Path2 call
            newAgentPath = self.AStar(currentAgent.currentNode, bestEndpoint, 0, currentAgent.numID)
            self.infoShareManager.handlePathPlanRequest(newAgentPath, currentAgent.numID)
            currentAgent.pathfinder.plannedPath = newAgentPath
            currentAgent.pathfinder.currentStep = 1
            # print(f"Agent{currentAgent.numID} planned: {newAgentPath}")
            return True
        for taskID, task in self.simTaskManager.taskList.items():
            if (task.dropoffNode == currentAgent.currentNode or task.pickupNode == currentAgent.currentNode) and task.taskStatus != "completed":
                # print(f"Agent is standing on an active task ({taskID}:{task.pickupNode}-{task.dropoffNode})endpoint, need to move")
                # The agent is standing on an active task's deposit or pickup node, blocking other agents from ever getting there
                # Find the nearest non-task endpoint
                winner = inf
                for endpoint in self.infoShareManager.V_ntask:
                    # Don't use already claimed endpoints
                    claimedEndpoints = [path[-1] for agent, path in self.infoShareManager.reservedPaths.items() if (not agent == currentAgent.numID)]
                    if endpoint in claimedEndpoints:
                        continue
                    taskDistance = self.infoShareManager.hScores[endpoint][currentAgent.currentNode]
                    if taskDistance < winner:
                        winner = taskDistance
                        bestEndpoint = endpoint
                # print(f"\tNearest free endpoint is {bestEndpoint}")
                # This is the Path2 call
                newAgentPath = self.AStar(currentAgent.currentNode, bestEndpoint, 0, currentAgent.numID)
                if newAgentPath == False:
                    return False
                self.infoShareManager.handlePathPlanRequest(newAgentPath, currentAgent.numID)
                currentAgent.pathfinder.plannedPath = newAgentPath
                currentAgent.pathfinder.currentStep = 1
                return bestEndpoint
        # Agent is fine to stay where it is
        if currentAgent.pathfinder is not None:
            stayInPlace = self.AStar(currentAgent.currentNode, currentAgent.currentNode, 0, currentAgent.numID)
            if stayInPlace == False:
                return False
            self.infoShareManager.handlePathPlanRequest(stayInPlace, currentAgent.numID)
            currentAgent.pathfinder.plannedPath = stayInPlace
            currentAgent.pathfinder.currentStep = 1
            pass
        return currentAgent.currentNode