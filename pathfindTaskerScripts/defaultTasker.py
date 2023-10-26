import random

class defaultTasker:
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
        for taskID, task in self.simTaskManager.taskList.items():
            if task.assignee is None and task.taskStatus == "unassigned":
                # Task is eligible for assignment
                self.simTaskManager.assignAgentToTask(taskID, currentAgent)
                taskRef = self.simTaskManager.taskList[taskID]
                self.canvasRef.requestRender("highlight", "new", {"targetNodeID": taskRef.pickupPosition,
                    "highlightType": "pickupHighlight", "multi": False, "highlightTags": ["task"+str(taskRef.numID)+"Highlight"]})
                self.canvasRef.requestRender("highlight", "new", {"targetNodeID": taskRef.dropoffPosition,
                    "highlightType": "depositHighlight", "multi": False, "highlightTags": ["task"+str(taskRef.numID)+"Highlight"]})
                return taskID
        # There were no suitable tasks
        return None