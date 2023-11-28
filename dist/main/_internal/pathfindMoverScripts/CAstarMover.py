import networkx as nx
from numpy import Inf

class CAstarMover:
    """
        The fallback method for handling agent collisions
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
        if agent.numID not in self.agentPriorityList:
            self.agentPriorityList.append(agent.numID)
        self.agentMotionDict[agent.numID] = desiredMove
        
    def checkAgentCollisions(self):
        # print("CHECKING AGENT COLLISIONS . . .")
        # print(self.agentMotionDict)

        # Check for conflicts
        vertexDict, edgeDict = self.comprehendAgentMotions()
        hasConflict = self.checkForConflicts(vertexDict, edgeDict)
        if hasConflict:
            conflictCount = 1
            return {"agents": hasConflict}
        else:
            conflictCount = 0
        # while hasConflict:
        #     # If there is a conflict, cycle the resolver until there isn't
        #     vertexDict, edgeDict = self.comprehendAgentMotions()
        #     hasConflict = self.checkForConflicts(vertexDict, edgeDict)
        # print(self.agentMotionDict)
        # print(">>>Conflict resolved, executing moves.")

        # After resolving conflicts, execute all the queued up movements
        for agent in self.agentPriorityList:
            currentAgent = self.agentManager.agentList[agent]
            self.simCanvasRef.requestRender("agent", "move", {"agentNumID": currentAgent.numID, 
                "sourceNodeID": currentAgent.currentNode, "targetNodeID": self.agentMotionDict[agent][1]})
            currentAgent.executeMove(self.agentMotionDict[agent][1])
            currentAgent.pathfinder.agentTookStep()

        # Reset the agent motion queue
        self.agentMotionDict = {}
        return conflictCount

    def comprehendAgentMotions(self):
        vertexDict = {}
        edgeDict = {}
        # print(self.agentPriorityList)

        # Decompose the list of agent desired actions into vertex and edge plan lists
        for agentID, agentMove in self.agentMotionDict.items():
            # self.sharedInfoManager.showReservationsByAgent(agentID)
            # print(f"{agentID}: {agentMove}")

            # Crashed agents need priority and a replan
            if agentMove == "crash":
                # Agent is completely blocked in, unable to avoid collision via reservation table
                # Examine neighbors to find the ideal movement for the agent
                currentAgent = self.agentManager.agentList[agentID]
                currentNode = currentAgent.currentNode
                neighbors = list(self.mapGraph.neighbors(currentNode)) + [currentNode]
                targetNode = currentAgent.returnTargetNode()
                # Default distance is infinite, such that any other distance is superior
                winnerDist = Inf
                for neighborNode in neighbors:
                    abstractDist = currentAgent.pathfinder.heuristicFunc(currentNode, targetNode)
                    if abstractDist < winnerDist:
                        winner = neighborNode
                        winnerDist = abstractDist
                agentMove = (currentNode, winner)
                # print(f"Agent crashed—prefers: {agentMove}")
                # Crashed units get top priority
                self.agentPriorityList.pop(self.agentPriorityList.index(agentID))
                self.agentPriorityList = [agentID] + self.agentPriorityList

                # Submit the new plan to the relevant trackers
                self.sharedInfoManager.handlePathPlanRequest([currentNode, winner], agentID)
                self.agentMotionDict[agentID] = agentMove
                
            # Vertex reservations are the destination node, in the next timestep
            if agentMove[1] in vertexDict:
                vertexDict[agentMove[1]].append(agentID)
            else:
                vertexDict[agentMove[1]] = [agentID]
            
            # Edges can be safely sorted such that A->B = A<-B
            edgeTuple = tuple(sorted(agentMove))
            if edgeTuple in edgeDict:
                edgeDict[edgeTuple].append(agentID)
            else:
                edgeDict[edgeTuple] = [agentID]
        return (vertexDict, edgeDict)
        
    def checkForConflicts(self, vertexDict, edgeDict):
        # print(f"V:{vertexDict}")
        # print(f"E:{edgeDict}")

        # Resolution preference is given to edge conflicts
        for edge, agents in edgeDict.items():
            if len(agents) > 1:
                self.conflictFound = True
                # print("EDGE CONFLICT")
                self.resolveEdgeConflict(agents[0], agents[1])
                # print(f"New motions: {self.agentMotionDict}")
                return agents

        for node, agents in vertexDict.items():
            if len(agents) > 1:
                self.conflictFound = True
                # print("VERTEX CONFLICT")
                self.resolveNodeConflict(agents)
                # print(f"New motions: {self.agentMotionDict}")
                return agents
        return False

    def resolveEdgeConflict(self, agentOne, agentTwo):
        # Priority driven; agent with higher priority (lower index) takes precedence
        agentList = [agentOne, agentTwo]
        for agentID in self.agentPriorityList:
            if agentID in agentList:
                # Found highest priority agent
                agentList.pop(agentList.index(agentID))
                break
        # print(f"\tCollision losers are: {agentList}")

        # Lower priority agents must replan around the locked-in higher priority agents
        for deprioAgent in agentList:
            # Find the object reference
            deprioAgentData = self.agentManager.agentList[deprioAgent]

            # Reset intended plan, then seek an open space to move away from the conflicts
            # Highest priority indicates the center of the collision knot, from which agents should disperse
            self.agentManager.agentList[deprioAgent].pathfinder.__reset__()
            deprioAgentNeighbors = self.findValidNeighbors(deprioAgentData)
            # print(f"Free neighbors: {deprioAgentNeighbors}")
            if len(deprioAgentNeighbors) == 0:
                # There's no free places to move, so check if there are valid overwrites
                self.agentManager.agentList[deprioAgentData.numID].pathfinder.__reset__()
                deprioAgentNeighbors = self.findLowerPriorityNeighbors(deprioAgentData)
                # print(f"Overwritable neighbors: {deprioAgentNeighbors}")
                # If there are no valid overwrites, the agent has literally zero options with this priority
                if len(deprioAgentNeighbors) == 0:
                    # print(f"Crashing...")
                    # If there are no valid free moves, and no valid overwrites, this agent needs highest priority
                    self.agentMotionDict[deprioAgent] = "crash"
                else:
                    # Otherwise, choose an overwrite and implement it
                    choice = deprioAgentNeighbors[0]
                    plannedPath = [deprioAgentData.currentNode, choice]
                    self.agentMotionDict[deprioAgentData.numID] = plannedPath
                    # Submit the new plan to the relevant trackers
                    deprioAgentData.pathfinder.plannedPath = plannedPath
                    self.sharedInfoManager.handlePathPlanRequest(plannedPath, deprioAgentData.numID)
            else:
                # Otherwise choose an overwrite and implement it
                choice = deprioAgentNeighbors[0]
                plannedPath = [deprioAgentData.currentNode, choice]
                self.agentMotionDict[deprioAgentData.numID] = plannedPath
                # Submit the new plan to the relevant trackers
                deprioAgentData.pathfinder.plannedPath = plannedPath
                self.sharedInfoManager.handlePathPlanRequest(plannedPath, deprioAgentData.numID)

    # def updateConflictingEdgePlans(self, prioAgent, deprioAgent):
    #     # Priority agent sets its desired path
    #     plannedPath = list(self.agentMotionDict[prioAgent.numID])
    #     prioAgent.pathfinder.plannedPath = plannedPath
    #     self.sharedInfoManager.handlePathPlanRequest(plannedPath, prioAgent.numID)

    #     # Deprio agent needs a new plan, selecting an immediate (free) neighbor
    #     deprioAgentNeighbors = self.findValidNeighbors(deprioAgent)
    #     choice = deprioAgentNeighbors[0]
    #     plannedPath = [deprioAgent.currentNode, choice]
    #     self.agentMotionDict[deprioAgent.numID] = plannedPath

    #     # Set the deprioritized agent path
    #     deprioAgent.pathfinder.plannedPath = plannedPath
    #     self.sharedInfoManager.handlePathPlanRequest(plannedPath, deprioAgent.numID)

    #     # Swap priorities in the priority list if necessary
    #     priorityAgentOldPrio = self.agentPriorityList.index(prioAgent.numID)
    #     depriorityAgentOldPrio = self.agentPriorityList.index(deprioAgent.numID)
    #     if priorityAgentOldPrio > depriorityAgentOldPrio:
    #         self.agentPriorityList[depriorityAgentOldPrio] = prioAgent.numID
    #         self.agentPriorityList[priorityAgentOldPrio] = deprioAgent.numID

    def resolveNodeConflict(self, agentList):
        # print(f"Conflicting agents: {agentList}")
        # Node conflicts resolve via priority order
        for agentID in self.agentPriorityList:
            if agentID in agentList:
                # Found highest priority agent
                plannedPath = list(self.agentMotionDict[agentID])
                deprioAgent = agentList.pop(agentList.index(agentID))
                deprioAgent = self.agentManager.agentList[deprioAgent]
                break
        # Remaining agents just try to wait in place
        agentList.reverse()
        for agent in agentList:
            # print(f"{agent} experiencing forced wait due to priority")
            # self.agentMustWait(agent)
            prioAgent = self.agentManager.agentList[agent]
            # Priority order needs shuffling in order to tie break and avoid deadlock
            self.swapAgentPriority(prioAgent, deprioAgent)

    def agentMustWait(self, agentID):
        # Agent will not move
        agent = self.agentManager.agentList[agentID]
        plannedPath = [agent.currentNode, agent.currentNode]
        
        # Release any prior path reservations
        agent.pathfinder.__reset__()

        # Submit the new path to the relevant trackers
        agent.pathfinder.plannedPath = plannedPath
        self.agentMotionDict[agent.numID] = tuple(plannedPath)
        self.sharedInfoManager.handlePathPlanRequest(plannedPath, agent.numID)

    def swapAgentPriority(self, prioAgent, deprioAgent):
        # Exchange the position in the priority list of the two passed agentIDs
        priorityAgentOldPrio = self.agentPriorityList.index(prioAgent.numID)
        depriorityAgentOldPrio = self.agentPriorityList.index(deprioAgent.numID)
        if priorityAgentOldPrio > depriorityAgentOldPrio:
            self.agentPriorityList[depriorityAgentOldPrio] = prioAgent.numID
            self.agentPriorityList[priorityAgentOldPrio] = deprioAgent.numID

    def findValidNeighbors(self, agentData):
        # print("Seeking free neighbors . . .")
        # Determine which neighboring nodes are available as-is
        validNeighbors = []
        neighbors = list(self.mapGraph.neighbors(agentData.currentNode))
        # Checking neighbors
        for i, neighbor in enumerate(neighbors):
            valid = self.sharedInfoManager.evaluateNodeEligibility(0, neighbor, agentData.currentNode, agentData.numID)
            if valid:
                validNeighbors.append(neighbor)
        # Checking own tile
        if self.sharedInfoManager.evaluateNodeEligibility(0, agentData.currentNode, agentData.currentNode, agentData.numID):
            validNeighbors.append(agentData.currentNode)
        return validNeighbors
    
    def findLowerPriorityNeighbors(self, agentData):
        # print(f"Seeking overwritable neighbors from {agentData.currentNode}")
        # print(self.agentPriorityList)
        # Determine which neighboring nodes are possible to overwrite
        validNeighbors = []
        neighbors = list(self.mapGraph.neighbors(agentData.currentNode))
        # If no valid free neighbors were found, then the agent needs to be willing to overwrite an agent's plan
        for i, neighbor in enumerate(neighbors):
            valid = self.sharedInfoManager.evaluateNodeOverwritability(0, neighbor, agentData.currentNode, agentData.numID, self.agentPriorityList)
            if valid:
                validNeighbors.append(neighbor)
        # Checking own tile
        if self.sharedInfoManager.evaluateNodeOverwritability(0, agentData.currentNode, agentData.currentNode, agentData.numID, self.agentPriorityList):
            validNeighbors.append(agentData.currentNode)
        # print(f"Agent needs to overwrite lower priority plans: {validNeighbors}")
        return validNeighbors