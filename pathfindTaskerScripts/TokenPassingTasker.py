import random
from numpy import inf

class TokenPassingTasker:
    """
        Fallback method for generating and assigning tasks
    """
    def __init__(self, pickupNodes, depositNodes, nodeWeights, validNodes, canvasRef, graphRef, infoShareManager, simAgentManager, simTaskManager):
        self.pickupNodes = pickupNodes
        self.depositNodes = depositNodes
        self.nodeWeights = nodeWeights
        self.validNodes = validNodes
        self.canvasRef = canvasRef
        self.graphRef = graphRef
        self.infoShareManager = infoShareManager
        self.simAgentManager = simAgentManager
        self.simTaskManager = simTaskManager

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
    
    def selectTaskForAgent(self, currentAgent):
        validTasks = []
        claimedEndpoints = []
        # The list of claimed endpoints is equivalent to the POIs for tasks that are not unassigned
        for taskID, task in self.simTaskManager.taskList.items():
            if task.assignee is not None:
                claimedEndpoints.append(task.pickupNode)
                claimedEndpoints.append(task.dropoffNode)
        # claimedEndpoints = [path[-1] for agent, path in self.infoShareManager.reservedPaths.items()]
        for taskID, task in self.simTaskManager.taskList.items():
            if task.assignee is None and task.taskStatus == "unassigned":
                # Task is eligible for assignment
                # print(f"Is task '{taskID}' node sj {task.pickupNode} or gj {task.dropoffNode} in...")
                # print(f"...{claimedEndpoints}")
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
        
    def handleAimlessAgent(self, currentAgent):
        # An agent is aimless if it does not have a target node (no task assigned)
        # In Token Passing, aimless agents need to make sure they are not on top of a task endpoint
        for taskID, task in self.simTaskManager.taskList.items():
            if task.dropoffNode == currentAgent.currentNode and task.taskStatus != "completed":
                # The agent is standing on an active task's deposit node
                # Find the nearest non-task endpoint
                winner = inf
                for endpoint in self.infoShareManager.V_ntask:
                    taskDistance = self.infoShareManager.hScores[endpoint][currentAgent.currentNode]
                    if taskDistance < winner:
                        winner = taskDistance
                        bestEndpoint = endpoint
                # This is the Path2 call
                # currentAgent.pathfinder.sourceNode = currentAgent.currentNode
                # currentAgent.pathfinder.targetNode = bestEndpoint
                currentAgent.targetNode = bestEndpoint
                currentAgent.pathfinder.__reset__()
                return bestEndpoint
        # Agent is fine to stay where it is
        if currentAgent.pathfinder is not None:
            # currentAgent.pathfinder.sourceNode = currentAgent.currentNode
            # currentAgent.pathfinder.targetNode = currentAgent.currentNode
            currentAgent.targetNode = currentAgent.currentNode
            currentAgent.pathfinder.__reset__()
            # currentAgent.pathfinder.plannedPath = [currentAgent.currentNode, currentAgent.currentNode]
            pass
        return currentAgent.currentNode