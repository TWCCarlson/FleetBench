import random
from numpy import inf
import pprint
pp = pprint.PrettyPrinter(indent=4)
from heapq import heappush, heappop
from itertools import count
from copy import deepcopy

class TPTSTasker:
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

    def generateTask(self, timeStamp=0):
        pickupNode = random.choice(list(self.pickupNodes.keys()))
        depositNode = random.choice(list(self.depositNodes.keys()))
        timeLimit = 0
        assignee = None
        taskStatus = "unassigned"

        newTaskID = self.simTaskManager.createNewTask(pickupNode=pickupNode, 
            dropoffNode=depositNode, timeLimit=timeLimit, assignee=assignee, taskStatus=taskStatus,
            timeStamp=timeStamp)
        # print(f">>>Created new task: {newTaskID}")
        return newTaskID
    
    def selectTaskForAgent(self, currentAgent, availableTaskSet=None, timeStamp=0):
        print(f"Fetching new task for agent{currentAgent.numID}")
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
        
        # pp.pprint(self.infoShareManager.reservedPaths)
        if availableTaskSet is None:
            availableTaskSet = []
            # Generate a list of the possible tasks (not yet executed)
            for taskID, task in self.simTaskManager.taskList.items():
                validStates = ["unassigned", "retrieving"]
                if task.taskStatus in validStates:
                    # print(f"Valid task: {taskID}")
                    availableTaskSet.append(taskID)

        # For all valid tasks in the tasklist, sort by proximity
        taskHeap = []
        for taskID in availableTaskSet:
            task = self.simTaskManager.taskList[taskID]
            hDist = self.infoShareManager.hScores[task.pickupNode][currentAgent.currentNode]
            heappush(taskHeap, (hDist, task.numID, task))

        while taskHeap:
            # print(f"{currentAgent.numID}:{taskHeap}")
            _, nextBestTaskID, nextBestTask = heappop(taskHeap)
            # print(f"Removing {nextBestTask.numID} from valid task set.")
            poppedTask = availableTaskSet.pop(availableTaskSet.index(nextBestTaskID))
            # print(f"=={poppedTask} removed.")
            occupied = False
            # Verify whether the task endpoints are available
            # print(f"Evaluating task {nextBestTask.numID}")
            # if nextBestTaskID == 98:
            #     print(f"\t{self.infoShareManager.reservedPaths.items()}")
            for agent, path in self.infoShareManager.reservedPaths.items():
                if agent == currentAgent.numID:
                    # print("\tFound own path, skipping")
                    # Ignore the path of the current agent
                    continue
                elif nextBestTask.assignee is not None and nextBestTask.assignee.numID == agent:
                    # print(f"\tFound previous assignee's ({agent}) path, skipping")
                    # Ignore the path of the currently assigned agent (we may overwrite this)
                    continue
                elif nextBestTask.pickupNode == path[-1] or nextBestTask.dropoffNode == path[-1]:
                    # print(f"\tFound reservation by another agent ({agent}), invalid task")
                    # Another agent is going to occupy this node, so this is not a good assignment
                    occupied = True
                    break
            if occupied:
                # Try a different task
                continue
            # print(f"\tTask {nextBestTask.numID} is valid, checking optimality...")
            if nextBestTask.assignee is not None:
                # Instance the old data in case it needs to be restored
                prevAssignee = nextBestTask.assignee
                prevAssigneePath = prevAssignee.pathfinder.plannedPath
                prevAssigneePathStep = prevAssignee.pathfinder.currentStep
                # Then the new agent's path is superior and it should steal the task
                # Free up the previous agent
                self.simTaskManager.unassignAgentFromTask(nextBestTask.numID, prevAssignee)
                # Transfer the task
                self.simTaskManager.assignAgentToTask(nextBestTask.numID, currentAgent)
                # Release its path
                prevAssignee.pathfinder.__reset__()
                prevAssignee.pathfinder.invalid = False
                # self.infoShareManager.handlePathRelease(prevAssigneePath[prevAssigneePathStep-1:], prevAssignee.numID)
                # prevAssignee.pathfinder.plannedPath = []
                # print(f"\t{currentAgent.numID}:Found competitor: {prevAssignee.numID}:")
                # print(f"\t\t w/ path: {prevAssigneePath}")
                # print(f"\t\t w/ path length: {prevAssigneePath.index(nextBestTask.pickupNode)-prevAssigneePathStep}")
                # Otherwise, try to find a path so that it can be evaluated for fastness
                newAssigneePickupPath = self.AStar(currentAgent.currentNode, nextBestTask.pickupNode, 0, currentAgent.numID, prevAssignee.numID)
                if newAssigneePickupPath is False:
                    # print("FAILED TO FIND PICKUP PATH")
                    # Failed to find a path to the task
                    self.simTaskManager.unassignAgentFromTask(nextBestTask.numID, currentAgent)
                    self.simTaskManager.assignAgentToTask(nextBestTask.numID, prevAssignee)
                    self.infoShareManager.handlePathPlanRequest(prevAssigneePath[prevAssigneePathStep-1:], prevAssignee.numID)
                    prevAssignee.pathfinder.plannedPath = prevAssigneePath
                    prevAssignee.pathfinder.currentStep = prevAssigneePathStep
                    continue
                # print(f"\tAgent {currentAgent.numID} could do it in {len(newAssigneePickupPath)}")
                # print(f"Old path: {prevAssigneePath}")
                if len(newAssigneePickupPath) < prevAssigneePath.index(nextBestTask.pickupNode)-prevAssigneePathStep:
                    # Complete the pathfinding operation for the new agent
                    # print(f"\tNew agent would win, completing path plan...")
                    newAssigneeDropoffPath = self.AStar(nextBestTask.pickupNode, nextBestTask.dropoffNode, len(newAssigneePickupPath)-1, currentAgent.numID, prevAssignee.numID)
                    if newAssigneeDropoffPath is False:
                        # print("FAILED TO FIND DELIVERY PATH")
                        # Failed to path to the dropoff point, revert unassignment
                        self.simTaskManager.unassignAgentFromTask(nextBestTask.numID, currentAgent)
                        self.simTaskManager.assignAgentToTask(nextBestTask.numID, prevAssignee)
                        self.infoShareManager.handlePathPlanRequest(prevAssigneePath[prevAssigneePathStep-1:], prevAssignee.numID)
                        prevAssignee.pathfinder.plannedPath = prevAssigneePath
                        prevAssignee.pathfinder.currentStep = prevAssigneePathStep
                        continue
                    
                    # Splice the paths
                    if self.simulationSettings["agentMiscOptionTaskInteractCostValue"] == "Pickup/dropoff require step":
                        # Path requires one extra step at the pickup location
                        newAssigneePath = newAssigneePickupPath + newAssigneeDropoffPath
                    else:
                        # Agent should move directly after reaching the pickup location
                        newAssigneePath = newAssigneePickupPath + newAssigneeDropoffPath[1:]
                    # print(f"!! Path plan: {newAssigneePath}")
                    # Reserve them
                    self.infoShareManager.handlePathPlanRequest(newAssigneePath, currentAgent.numID)
                    currentAgent.pathfinder.plannedPath = newAssigneePath
                    currentAgent.pathfinder.currentStep = 1
                    # The replaced agent now needs a new task
                    # print(f">>> Stole task from {prevAssignee.numID}, seeking replacement task...")
                    # print(f"\t...{availableTaskSet}")
                    if self.selectTaskForAgent(prevAssignee, availableTaskSet=deepcopy(availableTaskSet)):
                        # print(f"<<< gave {prevAssignee.numID} something to do :)")
                        return nextBestTask.numID
                    else:
                        # It was invalid because of something else down the line (replaced agent couldn't path to safety)
                        # print(f"<<< couldn't find a task :(")
                        self.simTaskManager.unassignAgentFromTask(nextBestTask.numID, currentAgent)
                        self.simTaskManager.assignAgentToTask(nextBestTask.numID, prevAssignee)
                        currentAgent.pathfinder.__reset__()
                        currentAgent.pathfinder.invalid = False
                        # self.infoShareManager.handlePathRelease(newAssigneePath, currentAgent.numID)
                        self.infoShareManager.handlePathPlanRequest(prevAssigneePath[prevAssigneePathStep-1:], prevAssignee.numID)
                        prevAssignee.pathfinder.plannedPath = prevAssigneePath
                        prevAssignee.pathfinder.currentStep = prevAssigneePathStep
                        availableTaskSet.append(poppedTask)
                        # print(availableTaskSet)
                        continue
                else:
                    # print(f"\tAgent would not be faster! Trying different task...")
                    self.simTaskManager.unassignAgentFromTask(nextBestTask.numID, currentAgent)
                    self.simTaskManager.assignAgentToTask(nextBestTask.numID, prevAssignee)
                    self.infoShareManager.handlePathPlanRequest(prevAssigneePath[prevAssigneePathStep-1:], prevAssignee.numID)
                    prevAssignee.pathfinder.plannedPath = prevAssigneePath
                    prevAssignee.pathfinder.currentStep = prevAssigneePathStep
                    # Agent is slower than the currently assigned agent, so move on
                    continue
            else:
                # print(f"{currentAgent.numID}:There was no competitor...")
                # Then the new agent can just take the task
                self.simTaskManager.assignAgentToTask(nextBestTask.numID, currentAgent, timeStamp)
                # print(f"{currentAgent.numID}: claiming task {nextBestTask.numID}")
                # Complete the pathfinding operation for the new agent
                newAssigneePickupPath = self.AStar(currentAgent.currentNode, nextBestTask.pickupNode, 0, currentAgent.numID)
                if newAssigneePickupPath == False:
                    self.simTaskManager.unassignAgentFromTask(nextBestTask.numID, currentAgent)
                    nextBestTask.serviceAssignTime = None
                    return False
                newAssigneeDropoffPath = self.AStar(nextBestTask.pickupNode, nextBestTask.dropoffNode, len(newAssigneePickupPath)-1, currentAgent.numID)
                # Splice the paths
                if self.simulationSettings["agentMiscOptionTaskInteractCostValue"] == "Pickup/dropoff require step":
                    # Path requires one extra step at the pickup location
                    newAssigneePath = newAssigneePickupPath + newAssigneeDropoffPath
                else:
                    # Agent should move directly after reaching the pickup location
                    newAssigneePath = newAssigneePickupPath + newAssigneeDropoffPath[1:]
                # Reserve them
                # print(f"New path: {newAssigneePath}")
                self.infoShareManager.handlePathPlanRequest(newAssigneePath, currentAgent.numID)
                currentAgent.pathfinder.plannedPath = newAssigneePath
                currentAgent.pathfinder.currentStep = 1
            # print(f"Assigned task {nextBestTask.numID} to agent {currentAgent.numID}!")
            return nextBestTask.numID
        # print("ran out of choices!")
        # An agent is aimless if it does not have a target node (no task assigned)
        # In Token Passing, aimless agents need to make sure they are not on top of a task endpoint
        if currentAgent.currentNode not in self.infoShareManager.V_endpoint:
            # print(f"Agent{currentAgent.numID} is not in an endpoint, finding nearest.")
            # Agent is not in an endpoint, needs to move to neareset one
            winner = inf
            # print(self.infoShareManager.V_ntask)
            for endpoint in self.infoShareManager.V_ntask:
                # Don't use already claimed endpoints
                claimedEndpoints = [path[-1] for agent, path in self.infoShareManager.reservedPaths.items() if (not agent == currentAgent.numID)]
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
        # Agent should attempt to find a free endpoint (path2)
        reservedEndpoints = [path[-1] for agent, path in self.infoShareManager.reservedPaths.items() if (not agent == currentAgent.numID)]
        taskPickupPoints = [task.pickupNode for taskID, task in self.simTaskManager.taskList.items() if not task.assignee == currentAgent]
        taskDeliveryPoints = [task.dropoffNode for taskID, task in self.simTaskManager.taskList.items() if not task.assignee == currentAgent]
        claimedEndpoints = reservedEndpoints + taskPickupPoints + taskDeliveryPoints
        if currentAgent.currentNode in claimedEndpoints:
            # Agent is standing on a task or claimed endpoint and needs to move
            winner = inf
            for endpoint in self.infoShareManager.V_ntask:
                if endpoint in claimedEndpoints:
                    continue
                hDistance = self.infoShareManager.hScores[endpoint][currentAgent.currentNode]
                if hDistance < winner:
                    winner = hDistance
                    bestEndpoint = endpoint
            # This is the path2 call
            newAgentPath = self.AStar(currentAgent.currentNode, bestEndpoint, 0, currentAgent.numID)
            if newAgentPath == False:
                return False
            self.infoShareManager.handlePathPlanRequest(newAgentPath, currentAgent.numID)
            currentAgent.pathfinder.plannedPath = newAgentPath
            currentAgent.pathfinder.currentStep = 1
            # print(f"Agent{currentAgent.numID} planned: {newAgentPath}")
            return True
        # for taskID, task in self.simTaskManager.taskList.items():
        #     # print(f"{taskID}>>{task.dropoffNode}vs{currentAgent.currentNode}:{task.dropoffNode == currentAgent.currentNode}?")
        #     # print(f"{taskID}>>{task.pickupNode}vs{currentAgent.currentNode}:{task.pickupNode == currentAgent.currentNode}?")
        #     # print(f"{taskID}>>Task active:{task.taskStatus}?")
        #     if (task.dropoffNode == currentAgent.currentNode or task.pickupNode == currentAgent.currentNode) and task.taskStatus != "completed":
        #         # print(f"Agent{currentAgent.numID} is standing on task {taskID}'s endpoint")
        #         # The agent is standing on an active task's deposit node
        #         # Find the nearest non-task endpoint
        #         winner = inf
        #         for endpoint in self.infoShareManager.V_ntask:
        #             claimedEndpoints = [path[-1] for agent, path in self.infoShareManager.reservedPaths.items() if (not agent == currentAgent.numID)]
        #             if endpoint in claimedEndpoints:
        #                 continue
        #             # Don't use already claimed endpoints
        #             taskDistance = self.infoShareManager.hScores[endpoint][currentAgent.currentNode]
        #             if taskDistance < winner:
        #                 winner = taskDistance
        #                 bestEndpoint = endpoint
        #         # This is the Path2 call
        #         newAgentPath = self.AStar(currentAgent.currentNode, bestEndpoint, 0, currentAgent.numID)
        #         if newAgentPath == False:
        #             return False
        #         self.infoShareManager.handlePathPlanRequest(newAgentPath, currentAgent.numID)
        #         currentAgent.pathfinder.plannedPath = newAgentPath
        #         currentAgent.pathfinder.currentStep = 1
        #         # print(f"Agent{currentAgent.numID} planned: {newAgentPath}")
        #         return True
        # Agent is fine to stay where it is
        # print(f"Agent{currentAgent.numID} is fine to stay where it is")
        if currentAgent.pathfinder is not None:
            stayInPlace = self.AStar(currentAgent.currentNode, currentAgent.currentNode, 0, currentAgent.numID)
            if stayInPlace == False:
                # print("Failed to stay in place.")
                return False
            self.infoShareManager.handlePathPlanRequest(stayInPlace, currentAgent.numID)
            currentAgent.pathfinder.plannedPath = stayInPlace
            currentAgent.pathfinder.currentStep = 1
            # print(f"Agent{currentAgent.numID} planned: {stayInPlace}")
            return True
        return False

    def AStar(self, sourceNode, targetNode, startTime, agentID, ignoredAgent=None):
        # print(f"{agentID} seeks {sourceNode}->{targetNode} from relative T{startTime}, ignoring {ignoredAgent}")
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
            # if agentID == 4:
            #     print(f"Exploring {currentNode} at T+{timeDepth}")
            #     print("?")
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
                # if agentID == 1:
                # print(f">>>Evaluate {currentNode}->{neighborNode}>>{targetNode}: {timeDepth}")
                if not self.infoShareManager.evaluateNodeEligibility(timeDepth, neighborNode, currentNode, agentID, ignoredAgent) and self.simulationSettings["agentCollisionsValue"] == "Respected":
                    # if agentID == 0:
                        # print(f"\tBlocked...")
                    # print(f"{agentID}: {neighborNode} Not eligible")
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

    def handleAimlessAgent(self, currentAgent):
        # An agent is aimless if it does not have a target node (no task assigned)
        # In Token Passing, aimless agents need to make sure they are not on top of a task endpoint
        if currentAgent.pathfinder.returnNextMove() is not None:
            # Let the agent keep going
            return
        if currentAgent.currentNode not in self.infoShareManager.V_endpoint:
            # print(f"Agent{currentAgent.numID} is not in an endpoint, finding nearest.")
            # Agent is not in an endpoint, needs to move to neareset one
            winner = inf
            # print(self.infoShareManager.V_ntask)
            for endpoint in self.infoShareManager.V_ntask:
                # Don't use already claimed endpoints
                claimedEndpoints = [path[-1] for agent, path in self.infoShareManager.reservedPaths.items() if (not agent == currentAgent.numID)]
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
        # Agent should attempt to find a free endpoint (path2)
        reservedEndpoints = [path[-1] for agent, path in self.infoShareManager.reservedPaths.items() if (not agent == currentAgent.numID)]
        taskPickupPoints = [task.pickupNode for taskID, task in self.simTaskManager.taskList.items() if not task.assignee == currentAgent]
        taskDeliveryPoints = [task.dropoffNode for taskID, task in self.simTaskManager.taskList.items() if not task.assignee == currentAgent]
        claimedEndpoints = reservedEndpoints + taskPickupPoints + taskDeliveryPoints
        if currentAgent.currentNode in claimedEndpoints:
            # Agent is standing on a task or claimed endpoint and needs to move
            winner = inf
            for endpoint in self.infoShareManager.V_ntask:
                if endpoint in claimedEndpoints:
                    continue
                hDistance = self.infoShareManager.hScores[endpoint][currentAgent.currentNode]
                if hDistance < winner:
                    winner = hDistance
                    bestEndpoint = endpoint
            # This is the path2 call
            newAgentPath = self.AStar(currentAgent.currentNode, bestEndpoint, 0, currentAgent.numID)
            if newAgentPath == False:
                return False
            self.infoShareManager.handlePathPlanRequest(newAgentPath, currentAgent.numID)
            currentAgent.pathfinder.plannedPath = newAgentPath
            currentAgent.pathfinder.currentStep = 1
            # print(f"Agent{currentAgent.numID} planned: {newAgentPath}")
            return True
        # Agent is fine to stay where it is
        if currentAgent.pathfinder is not None:
            stayInPlace = self.AStar(currentAgent.currentNode, currentAgent.currentNode, 0, currentAgent.numID)
            if stayInPlace == False:
                return False
            self.infoShareManager.handlePathPlanRequest(stayInPlace, currentAgent.numID)
            currentAgent.pathfinder.plannedPath = stayInPlace
            currentAgent.pathfinder.currentStep = 1
        return currentAgent.currentNode