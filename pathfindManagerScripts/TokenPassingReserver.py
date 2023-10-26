import networkx as nx
import pprint
pp = pprint.PrettyPrinter(indent=4)
from itertools import count
from copy import deepcopy


class TokenPassingReserver:
    """
        Class which manages the token in the Token Passing algorithm
    """
    def __init__(self, mapGraph):
        # Store the base graph
        self.mapGraphRef = mapGraph

    def build(self):
        self.graphStructure = nx.Graph()
        self.graphStructure.add_nodes_from(self.mapGraphRef.nodes(data=False))
        self.graphStructure.add_edges_from(self.mapGraphRef.edges(data=False))
        # Token Passing features a very heavy precompute step
        # All "endpoints" must be collected
        # Shortest paths from all nodes to each endpoint are then calculated and stored
        # This eliminates the need to compute the heuristic distance when pathfinding

        # Find all endpoints and sort them
        self.V_task = []
        self.V_ntask = []
        self.V_endpoint = []
        for node, nodeData in self.mapGraphRef.nodes(data=True):
            if nodeData["type"] in ["deposit", "pickup"]:
                # Node is a task endpoint
                self.V_task.append(node)
            elif nodeData["type"] in ["rest", "charge"]:
                # Node is a non-task endpoint
                self.V_ntask.append(node)
            else:
                # Node is not an endpoint
                pass
            V_endpoint = self.V_task + self.V_ntask
        
        # Compute the heuristic distances from all nodes to all endpoints
        # Only allow the use of manhattan for guiding the search
        self.hScores = {}
        def heuristic(u, v):
            # Manhattan/taxicab distance is the absolute value of the difference 
            uPos = self.mapGraphRef.nodes[u]['pos']
            vPos = self.mapGraphRef.nodes[v]['pos']
            heuristicDistance = abs(uPos['X']-vPos['X']) + abs(uPos['Y']-vPos['Y'])
            return heuristicDistance
        for sourceNode in self.mapGraphRef.nodes(data=False):
            for targetNode in V_endpoint:
                if targetNode not in self.hScores.keys():
                    self.hScores[targetNode] = {}
                distance = nx.astar_path_length(self.graphStructure, sourceNode, targetNode, heuristic=heuristic)
                self.hScores[targetNode][sourceNode] = distance

        # for targetNode in self.hScores.keys():
        #     print(f"{targetNode}")
        #     print(f"{self.hScores[targetNode].items()}")
        # Initialize the token
        self.currentDepth = 0
        self.initializeToken()

    def updateSimulationDepth(self, currentDepth):
        # The current simulation step is stored as an offset for any future calls
        self.currentDepth = currentDepth

    def purgePastData(self):
        pass

    def evaluateNodeEligibility(self, timeDepth, targetNode, sourceNode, agentID):
        # print(f"Searching at {timeDepth+self.currentDepth}")
        # Verifies if the node is open at a specific time
        # Expands the reservation table if the request depth exceeds the table's depth
        if timeDepth + self.currentDepth >= self.timeTracked:
            self.expandReservationTable(timeDepth + self.currentDepth)
            # print(f"New depth: {timeDepth+self.currentDepth}")
            # print(f"{self.__sizeof__()}")
        
        # If the agent is considering a "wait" move, where it does not move
        # print(targetNode)
        # print(sourceNode)
        if targetNode == sourceNode:
            # Have to check all edges leading to this node, and the future node
            edgeReserved = False
            for node in self.reservationTable[timeDepth+self.currentDepth][sourceNode]:
                edgeReserved = edgeReserved or self.getEdgeState(timeDepth+self.currentDepth, sourceNode, node, agentID)
            nodeReserved = self.getNodeState(timeDepth+self.currentDepth+1, sourceNode, agentID)
        else:
            edgeReserved = self.getEdgeState(timeDepth + self.currentDepth, sourceNode, targetNode, agentID)
            nodeReserved = self.getNodeState(timeDepth + self.currentDepth + 1, targetNode, agentID)
        if not nodeReserved and not edgeReserved:
            # print(f"{targetNode} in {timeDepth} from now ({timeDepth+self.currentDepth}) is accessible.")
            # Node is occupied and ineligible for use in pathfinding
            return True
        elif nodeReserved:
            # print(f"<<<{targetNode} in {timeDepth} from now ({timeDepth+self.currentDepth}) is NODE BLOCKED.")
            return False
        elif edgeReserved:
            # print(f"<<<{targetNode} in {timeDepth} from now ({timeDepth+self.currentDepth}) is EDGE BLOCKED")
            return False
        
    def evaluateEndpointEligibility(self, timeDepth, targetNode, agentID):
        # Endpoints need to be available all the way through the time horizon
        # print(f"Checking that endpoint is available from {timeDepth}-{self.timeTracked}")
        timeStepsToCheck = range(timeDepth+self.currentDepth, self.timeTracked)
        # print(timeStepsToCheck)
        for depth in timeStepsToCheck:
            nodeReserved = self.getNodeState(depth, targetNode, agentID)
            if nodeReserved is True:
                # print(f"Node {targetNode} is reserved at {depth} by {self.getNodeReserver(depth, targetNode)}, have to wait")
                return False
        return True

    def initializeToken(self):
        # Build the table for depth 0
        self.reservationTable = {
            0: deepcopy(self.graphStructure),
        }

        # Preallocate nodes as being unreserved
        self.preallocNodes(0)
        self.preallocEdges(0)

        # Instantiate a counter that tracks the forward progression of time
        self.depthCounter = count()
        self.timeTracked = next(self.depthCounter)

        # Container for agent paths, used to check for endpoint availability
        self.reservedPaths = {}

    def handlePathPlanRequest(self, requestedNodeList, agentID):
        # Reserves nodes and edges for the found path, starting from currentDepth
        for depth, node in enumerate(requestedNodeList[1:]):
            # Reserve the edge at this time step
            self.reserveEdge(depth+self.currentDepth, requestedNodeList[depth], node, agentID)
            # Reserve the node at the next time step
            self.reserveNode(depth+self.currentDepth+1, node, agentID)
        # Note down the path for access by other agents
        self.reservedPaths[agentID] = requestedNodeList

    def handlePathRelease(self, requestedNodeList, agentID):
        # print(f"Releasing: {requestedNodeList} from {self.currentDepth}")
        # Releases nodes and edges for the provided path, starting from currentDepth
        for depth, node in enumerate(requestedNodeList[1:]):
            # print(f"{requestedNodeList[depth]}->{node} @ {self.currentDepth+depth}")
            # Release the edge at this time step
            self.releaseEdge(depth+self.currentDepth, requestedNodeList[depth], node, agentID)
            # Release the node at the next time step
            self.releaseNode(depth+self.currentDepth+1, node, agentID)
            # print(f"Released {node}")
            # pp.pprint(self.reservationTable[depth+self.currentDepth+1].nodes(data=True))
        # self.showReservationsByAgent(agentID)
        # Release the idea of a path too
        if agentID in self.reservedPaths:
            del self.reservedPaths[agentID]

    def reserveNode(self, timeStep, node, agentID):
        self.reservationTable[timeStep].nodes[node]["Reserved"] = str(agentID)

    def reserveEdge(self, timeStep, sourceNode, targetNode, agentID):
        # If the agent's plan is to wait, then all neighboring edges need to be reserved
        if sourceNode == targetNode:
            # for neighbor in self.reservationTable[timeStep][sourceNode]:
            #     self.reservationTable[timeStep][sourceNode][neighbor]["Reserved"] = str(agentID)
            pass
        else:
            self.reservationTable[timeStep][sourceNode][targetNode]["Reserved"] = str(agentID)

    def releaseNode(self, timeStep, node, agentID):
        # print(f"\tRelease node: {node} @ {timeStep}")
        # print(f"\t{self.reservationTable[timeStep].nodes[node]['Reserved']}")
        if self.reservationTable[timeStep].nodes[node]["Reserved"] == str(agentID):
            # print(f"\t node released")
            self.reservationTable[timeStep].nodes[node]["Reserved"] = False

    def releaseEdge(self, timeStep, sourceNode, targetNode, agentID):
        # print(f"\tRelease edge: {sourceNode}->{targetNode} @ {timeStep}")
        if sourceNode == targetNode:
            # print(f"\t same tile, no edge release needed")
            pass
        else:
            # print(f"\t{self.reservationTable[timeStep][sourceNode][targetNode]['Reserved']}")
            if self.reservationTable[timeStep][sourceNode][targetNode]["Reserved"] == str(agentID):
                # print(f"\t edge released")
                self.reservationTable[timeStep][sourceNode][targetNode]["Reserved"] = False

    def getNodeState(self, timeStep, node, agentID):
        # Nodes can be outright reserved:
        reserver = self.reservationTable[timeStep].nodes[node]["Reserved"]
        # print(f"Node: {self.reservationTable[timeStep].nodes[node]['Reserved']}; {bool(self.reservationTable[timeStep].nodes[node]['Reserved'])}")
        # if reserver == str(agentID):
        #     # print("Node reserved by self.")
        #     return False
        # elif reserver == False:
        #     return False
        # else:
        #     # print("Node reserved by another.")
        #     return True
        
        # In token passing, it is also assumed that the end of agent paths is reserved:
        claimedEndpoints = [path[-1] for agent, path in self.reservedPaths.items() if not agent == agentID]
        #### ^^^^^^ needs to exclude agents own endpoint or else it cannot stay in place

        validReserveStates = [str(agentID), False]
        if node in claimedEndpoints or reserver not in validReserveStates:
            # print(f"Node is not available")
            # if agentID == 6 or agentID == 1:
            #     # print(node in claimedEndpoints)
            #     # print(claimedEndpoints)
            #     # print(reserver not in validReserveStates)
            #     # print(reserver)
            return True
        elif not node in claimedEndpoints:
            # if agentID == 6 or agentID == 1:
            #     print("node endpoint is not claimed")
            return False
        elif reserver in validReserveStates:
            # if agentID == 6 or agentID == 1:
            #     print("node is not reserved")
            return False
        
    def getNodeReserver(self, timeStep, node):
        reserver = self.reservationTable[timeStep].nodes[node]["Reserved"]
        # print(f"\t{reserver}")
        # print(self.reservationTable[timeStep].nodes(data=True))
        return reserver

    def getEdgeState(self, timeStep, sourceNode, targetNode, agentID):
        reserver = self.reservationTable[timeStep][sourceNode][targetNode]["Reserved"]
        # print(f"Edge: {self.reservationTable[timeStep][sourceNode][targetNode]['Reserved']}; {bool(self.reservationTable[timeStep][sourceNode][targetNode]['Reserved'])}")
        if reserver == str(agentID):
            # print("Edge reserved by self.")
            return False
        elif reserver == False:
            return False
        else:
            # print("Edge reserved by another.")
            return True
        
    def getEdgeReserver(self, timeStep, sourceNode, targetNode):
        if sourceNode == targetNode:
            # There is no edge between timesteps
            return False
        else:
            reserver = self.reservationTable[timeStep][sourceNode][targetNode]["Reserved"]
        return reserver

    def expandReservationTable(self, timeDepth):
        self.reservationTable[timeDepth+1] = deepcopy(self.graphStructure)
        self.preallocNodes(timeDepth+1)
        self.preallocEdges(timeDepth+1)
        self.timeTracked = next(self.depthCounter)

    def preallocNodes(self, timeDepth):
        nx.set_node_attributes(self.reservationTable[timeDepth], False, "Reserved")

    def preallocEdges(self, timeDepth):
        nx.set_edge_attributes(self.reservationTable[timeDepth], False, "Reserved")