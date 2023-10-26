import networkx as nx

class TokenPassingMover:
    """
        Executes moves provided by the token passing algorithm
    """
    def __init__(self, mapCanvas, mapGraph, sharedInfoManager, agentManager, taskManager, simCanvasRef):
        self.mapCanvas = mapCanvas
        self.mapGraph = mapGraph
        self.sharedInfoManager = sharedInfoManager
        self.agentManager = agentManager
        self.taskManager = taskManager
        self.simCanvasRef = simCanvasRef

        # Necessary, but unused
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
        # Check for conflicts
        vertexDict, edgeDict = self.comprehendAgentMotions()
        hasConflict = self.checkForConflicts(vertexDict, edgeDict)
        # Moves are rubberstamped due to TP Property 1
        for agent in self.agentPriorityList:
            currentAgent = self.agentManager.agentList[agent]
            self.simCanvasRef.requestRender("agent", "move", {"agentNumID": currentAgent.numID, 
                "sourceNodeID": currentAgent.currentNode, "targetNodeID": self.agentMotionDict[agent][1]})
            currentAgent.executeMove(self.agentMotionDict[agent][1])
            currentAgent.pathfinder.agentTookStep()
        pass

    def comprehendAgentMotions(self):
        vertexDict = {}
        edgeDict = {}
        # print(self.agentPriorityList)

        # Decompose the list of agent desired actions into vertex and edge plan lists
        for agentID, agentMove in self.agentMotionDict.items():
            # self.sharedInfoManager.showReservationsByAgent(agentID)
            # print(f"{agentID}: {agentMove}")

            # Crashed agents need priority and a replan
            # if agentMove == "crash":
            #     # Agent is completely blocked in, unable to avoid collision via reservation table
            #     # Examine neighbors to find the ideal movement for the agent
            #     currentAgent = self.agentManager.agentList[agentID]
            #     currentNode = currentAgent.currentNode
            #     neighbors = list(self.mapGraph.neighbors(currentNode)) + [currentNode]
            #     targetNode = currentAgent.returnTargetNode()
            #     # Default distance is infinite, such that any other distance is superior
            #     winnerDist = Inf
            #     for neighborNode in neighbors:
            #         abstractDist = currentAgent.pathfinder.heuristicFunc(currentNode, targetNode)
            #         if abstractDist < winnerDist:
            #             winner = neighborNode
            #             winnerDist = abstractDist
            #     agentMove = (currentNode, winner)
            #     # print(f"Agent crashed—prefers: {agentMove}")
            #     # Crashed units get top priority
            #     self.agentPriorityList.pop(self.agentPriorityList.index(agentID))
            #     self.agentPriorityList = [agentID] + self.agentPriorityList

            #     # Submit the new plan to the relevant trackers
            #     self.sharedInfoManager.handlePathPlanRequest([currentNode, winner], agentID)
            #     self.agentMotionDict[agentID] = agentMove
                
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
                print("EDGE CONFLICT")
                raise ValueError
                # self.resolveEdgeConflict(agents[0], agents[1])
                # print(f"New motions: {self.agentMotionDict}")
                return True

        for node, agents in vertexDict.items():
            if len(agents) > 1:
                self.conflictFound = True
                print("VERTEX CONFLICT")
                raise ValueError
                # self.resolveNodeConflict(agents)
                # print(f"New motions: {self.agentMotionDict}")
                return True
        return False