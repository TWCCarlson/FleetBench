import networkx as nx
from numpy import Inf

class WHCAstarMover:
    """
        Class responsible for handling the movement validation and execution of agents
    """
    def __init__(self, mapCanvas, mapGraph, sharedInfoManager, agentManager, taskManager, simCanvasRef):
        self.mapCanvas = mapCanvas
        self.mapGraph = mapGraph
        self.sharedInfoManager = sharedInfoManager
        self.agentManager = agentManager
        self.taskManager = taskManager
        self.simCanvasRef = simCanvasRef

        # Collision manager uses a list of submitted moves, arriving in order of priority
        self.agentPriorityList = []
        self.agentMotionDict = {}

    def getCurrentPriorityOrder(self):
        return self.agentPriorityList
    
    def setCurrentPriorityOrder(self, newPriorityList):
        self.agentPriorityList = newPriorityList

    def resetCurrentPriorityOrder(self):
        self.agentPriorityList = []
    
    def submitAgentAction(self, agent, desiredMove):
        self.agentPriorityList.append(agent.numID)
        self.agentMotionDict[agent.numID] = desiredMove
        
    def checkAgentCollisions(self):
        # print("CHECKING AGENT COLLISIONS . . .")
        # print(self.agentMotionDict)
        vertexDict, edgeDict = self.comprehendAgentMotions()
        self.checkForConflicts(vertexDict, edgeDict)
        # print(self.agentMotionDict)
        # print(">>>Conflict resolved, executing moves.")
        for agent in self.agentPriorityList:
            currentAgent = self.agentManager.agentList[agent]
            self.simCanvasRef.requestRender("agent", "move", {"agentNumID": currentAgent.numID, 
                "sourceNodeID": currentAgent.currentNode, "targetNodeID": self.agentMotionDict[agent][1]})
            currentAgent.executeMove(self.agentMotionDict[agent][1])

        # Reset the agent motion queue
        self.agentMotionDict = {}

    def comprehendAgentMotions(self):
        vertexDict = {}
        edgeDict = {}
        # Decompose the list of agent desired actions into vertex and edge plan lists
        for agentID, agentMove in self.agentMotionDict.items():
            # print(f"{agentID}: {agentMove}")
            if agentMove == "crash":
                # Agent is completely blocked in, unable to avoid collision via reservation table
                # Examine neighbors to find the ideal movement for the agent
                currentNode = self.agentManager.agentList[agentID].currentNode
                neighbors = list(self.mapGraph.neighbors(currentNode)) + [currentNode]
                targetNode = self.agentManager.agentList[agentID].returnTargetNode()
                winnerDist = Inf
                for neighborNode in neighbors:
                    abstractDist = self.sharedInfoManager.calculateHeuristicDistance(neighborNode, targetNode, "Manhattan")
                    if abstractDist < winnerDist:
                        winner = neighborNode
                        winnerDist = abstractDist
                agentMove = (currentNode, winner)
                # print(f"Agent crashed—prefers: {agentMove}")
                self.agentMotionDict[agentID] = agentMove
                
            # Vertex reservations are the destination node, in the next timestep
            if agentMove[1] in vertexDict:
                vertexDict[agentMove[1]].append(agentID)
            else:
                vertexDict[agentMove[1]] = [agentID]
            # Edge reservations are the combination of start and destination nodes, sorted by ID
            edgeTuple = tuple(sorted(agentMove))
            if edgeTuple in edgeDict:
                edgeDict[edgeTuple].append(agentID)
            else:
                edgeDict[edgeTuple] = [agentID]
        return (vertexDict, edgeDict)
        
    def checkForConflicts(self, vertexDict, edgeDict):
        # Resolution preference is given to edge conflicts
        for edge, agents in edgeDict.items():
            if len(agents) > 1:
                self.conflictFound = True
                # print("EDGE CONFLICT")
                self.resolveEdgeConflict(agents[0], agents[1])
                vertexDict, edgeDict = self.comprehendAgentMotions()
                self.checkForConflicts(vertexDict, edgeDict)

        for node, agents in vertexDict.items():
            if len(agents) > 1:
                self.conflictFound = True
                # print("VERTEX CONFLICT")
                self.resolveNodeConflict(agents)
                vertexDict, edgeDict = self.comprehendAgentMotions()
                self.checkForConflicts(vertexDict, edgeDict)

    def resolveEdgeConflict(self, agentOne, agentTwo):
        agentOneData = self.agentManager.agentList[agentOne]
        agentTwoData = self.agentManager.agentList[agentTwo]
        # Both agents need to unreserve from the table
        agentOneData.pathfinder.__reset__()
        agentTwoData.pathfinder.__reset__()
        # Find the number of valid neighbor nodes there are for each agent
        agentOneNeighbors = self.findValidNeighbors(agentOneData)
        agentTwoNeighbors = self.findValidNeighbors(agentTwoData)
        # print(f"Agent '{agentOne}' has: {len(agentOneNeighbors)-1} choices; agent '{agentTwo}' has: {len(agentTwoNeighbors)-1}")
        if len(agentOneNeighbors) < len(agentTwoNeighbors):
            self.updateConflictingEdgePlans(prioAgent=agentOneData, deprioAgent=agentTwoData)
        elif len(agentTwoNeighbors) < len(agentOneNeighbors):
            self.updateConflictingEdgePlans(prioAgent=agentTwoData, deprioAgent=agentOneData)
        elif len(agentOneNeighbors) == 0 and len(agentTwoNeighbors) == 0:
            # Both agents have nowhere to go
            # Aside from the trivial situation where there are only two nodes and two agents in the graph,
            # this only occurs when some other reservation is preventing either from moving.
            # Thus, both should wait in place.
            self.agentMustWait(agentOne)
            self.agentMustWait(agentTwo)
        # print(self.agentPriorityList)

    def updateConflictingEdgePlans(self, prioAgent, deprioAgent):
        # Priority agent sets its desired path
        plannedPath = list(self.agentMotionDict[prioAgent.numID])
        prioAgent.pathfinder.plannedPath = plannedPath
        self.sharedInfoManager.handlePathPlanRequest(plannedPath, prioAgent.numID)

        # Deprio agent needs a new plan, selecting an immediate (free) neighbor
        deprioAgentNeighbors = self.findValidNeighbors(deprioAgent)
        choice = deprioAgentNeighbors[0]
        plannedPath = [deprioAgent.currentNode, choice]
        self.agentMotionDict[deprioAgent.numID] = plannedPath

        # Set the deprioritized agent path
        deprioAgent.pathfinder.plannedPath = plannedPath
        self.sharedInfoManager.handlePathPlanRequest(plannedPath, deprioAgent.numID)

        # Swap priorities in the priority list if necessary
        priorityAgentOldPrio = self.agentPriorityList.index(prioAgent.numID)
        depriorityAgentOldPrio = self.agentPriorityList.index(deprioAgent.numID)
        if priorityAgentOldPrio > depriorityAgentOldPrio:
            self.agentPriorityList[depriorityAgentOldPrio] = prioAgent.numID
            self.agentPriorityList[priorityAgentOldPrio] = deprioAgent.numID

    def agentMustWait(self, agent):
        agent = self.agentManager.agentList[agent]
        plannedPath = [agent.currentNode, agent.currentNode]
        agent.pathfinder.plannedPath = plannedPath
        self.sharedInfoManager.handlePathPlanRequest(plannedPath, agent.numID)

    def resolveNodeConflict(self, agentList):
        # Node conflicts resolve via priority order, with lower priority agents being forced to wait in place
        for agentID in self.agentPriorityList:
            if agentID in agentList:
                # Found highest priority agent
                plannedPath = list(self.agentMotionDict[agentID])
                agentList.pop(agentList.index(agentID))
        # Remaining agents just try to wait in place
        for agent in agentList:
            self.agentMustWait(agent)

    def findValidNeighbors(self, agentData):
        validNeighbors = []
        neighbors = self.mapGraph.neighbors(agentData.currentNode)
        for i, neighbor in enumerate(neighbors):
            valid = self.sharedInfoManager.evaluateNodeEligibility(0, neighbor, agentData.currentNode, agentData.numID)
            if valid:
                validNeighbors.append(neighbor)
        return validNeighbors