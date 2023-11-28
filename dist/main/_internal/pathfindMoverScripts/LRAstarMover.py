import networkx as nx
from numpy import Inf

class LRAstarMover:
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
        # Immediately perform the move
        if agent.numID not in self.agentPriorityList:
            self.agentPriorityList.append(agent.numID)
        self.agentMotionDict[agent.numID] = desiredMove
        # print(f"{agent.numID}:{desiredMove}")
        # print(self.agentMotionDict)
        vertexDict, edgeDict = self.comprehendAgentMotions()
        conflicts = self.checkForConflicts(vertexDict, edgeDict)
        if conflicts is None and desiredMove is not "crash":
            if "agent" not in self.mapGraph.nodes(data=True)[desiredMove[1]] or agent == self.mapGraph.nodes(data=True)[desiredMove[1]]["agent"]:
                self.simCanvasRef.requestRender("agent", "move", {"agentNumID": agent.numID, 
                    "sourceNodeID": agent.currentNode, "targetNodeID": self.agentMotionDict[agent.numID][1]})
                agent.executeMove(self.agentMotionDict[agent.numID][1])
                agent.pathfinder.agentTookStep()
                return True
            else:
                self.agentManager.agentList[agent.numID].pathfinder.__reset__()
                return False
        else:
            # A different action needs to be taken
            self.agentManager.agentList[agent.numID].pathfinder.__reset__()
            return False

    def checkAgentCollisions(self):
        self.agentMotionDict = {}
        return None

    def comprehendAgentMotions(self):
        vertexDict = {}
        edgeDict = {}
        # Decompose the list of agent desired actions into vertex and edge plan lists
        for agentID, agentMove in self.agentMotionDict.items():
            # print(f"{agentID}: {agentMove}")
            if agentMove == "crash":
                # Agent failed to find a path, so it waits in place
                currentNode = self.agentManager.agentList[agentID].currentNode
                agentMove = (currentNode, currentNode)
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
                # Force a replan by returning an incomplete action list
                return ("crash", agents)

        for node, agents in vertexDict.items():
            if len(agents) > 1:
                self.conflictFound = True
                # print("VERTEX CONFLICT")
                # Force a replan by returning an incomplete action list
                # Higher priority agent should just move in
                plannedPath = list(self.agentMotionDict[agents[0]])
                otherAgents = agents[1:]
                return ("crash", otherAgents)
            