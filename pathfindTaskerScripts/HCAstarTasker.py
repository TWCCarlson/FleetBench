import random
from heapq import heappop, heappush
from itertools import count
from numpy import Inf

class HCAstarTasker:
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
        return newTaskID
    
    def selectTaskForAgent(self, currentAgent, timeStamp=0):
        for taskID, task in self.simTaskManager.taskList.items():
            if task.assignee is None and task.taskStatus == "unassigned":
                # Task is eligible for assignment
                self.simTaskManager.assignAgentToTask(taskID, currentAgent, timeStamp)
                taskRef = self.simTaskManager.taskList[taskID]
                self.canvasRef.requestRender("highlight", "new", {"targetNodeID": taskRef.pickupPosition,
                    "highlightType": "pickupHighlight", "multi": False, "highlightTags": ["task"+str(taskRef.numID)+"Highlight"]})
                self.canvasRef.requestRender("highlight", "new", {"targetNodeID": taskRef.dropoffPosition,
                    "highlightType": "depositHighlight", "multi": False, "highlightTags": ["task"+str(taskRef.numID)+"Highlight"]})
                return taskID
        # There were no suitable tasks
        return None

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
        fScore[(sourceNode, startTime)] = self.simAgentManager.agentList[agentID].pathfinder.heuristicFunc(sourceNode, targetNode)
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
                self.infoShareManager.handlePathPlanRequest(path, agentID)
                return path
            # If not, examine successors
            neighborNodes = list(self.graphRef.neighbors(currentNode)) + [currentNode]
            for neighborNode in neighborNodes:
                # if agentID == 1:
                    # print(f">>>Evaluate {currentNode}->{neighborNode}>>{targetNode}: {timeDepth}")
                if not self.infoShareManager.evaluateNodeEligibility(timeDepth, neighborNode, currentNode, agentID) and self.simulationSettings["agentCollisionsValue"] == "Respected":
                    # if agentID == 0:
                        # print(f"\tBlocked...")
                    # print(f"{agentID}: {neighborNode} Not eligible")
                    # Node is blocked, but if its an agent we want to ignore that is fine
                    continue
                # Node g scores increase by "weight" per step
                est_gScore = gScore[(currentNode, timeDepth)] + weight
                # If this estimated gScore is an improvement over the existing value (default infinity for unexpanded nodes)
                if est_gScore < gScore.get((neighborNode, timeDepth+1), Inf):
                    # Then a new best path to this node has been found
                    cameFrom[(neighborNode, timeDepth+1)] = (currentNode, timeDepth)
                    # Record the new gScore
                    gScore[(neighborNode, timeDepth+1)] = est_gScore
                    # Calculate nodes estimated distance from the goal
                    hScore = self.infoShareManager.calculateHeuristicDistance(neighborNode, targetNode, self.simAgentManager.agentList[agentID].pathfinder.heuristicFunc)
                    # Calculate the fScore for the new node
                    node_fScore = est_gScore + hScore
                    # If the node isn't in the openSet, it should be added
                    if (neighborNode, timeDepth+1) not in fScore:
                        heappush(openSet, (node_fScore, next(counter), neighborNode, timeDepth+1))
                    # Update the node's fScore
                    fScore[(neighborNode, timeDepth+1)] = node_fScore
        return False

    def handleAimlessAgent(self, currentAgent):
        # Default behavior for agents with no objective is to wait in place
        # It is the job of the algorithm to deal with agents when they cannot
        # currentAgent.pathfinder.__reset__()
        currentAgent.pathfinder.plannedPath = self.AStar(currentAgent.currentNode, currentAgent.currentNode, 0, currentAgent.numID)
        currentAgent.pathfinder.currentStep = 1
        return currentAgent.currentNode