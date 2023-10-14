import networkx as nx
import numpy as np
import pprint
pp = pprint.PrettyPrinter(indent=4)
import sys
from copy import deepcopy
from itertools import count
from numpy import inf
from numpy import sqrt
from heapq import heappop, heappush

class WHCAstarReserver:
    """
        Class which maintains a "reservation table for the cooperative A* technique
    """
    def __init__(self, mapGraph):
        # Store the base graph
        self.mapGraphRef = mapGraph
        self.RRAdata = {}
        self.heuristicFunc = None
        self.heuristicCoefficient = None
    
    def build(self):
        self.graphStructure = nx.Graph()
        # Add nodes, remove data
        self.graphStructure.add_nodes_from(self.mapGraphRef.nodes(data=False))
        self.graphStructure.add_edges_from(self.mapGraphRef.edges(data=False))

        # Start the current offset at time t=0
        self.currentDepth = 0

        # Initialize the reservation table
        self.createReservationTable()

    def updateSimulationDepth(self, currentDepth):
        # The current simulation step is stored as an offset for any future calls
        self.currentDepth = currentDepth

    def purgePastData(self):
        pass

    def evaluateNodeEligibility(self, timeDepth, targetNode, sourceNode):
        # Verifies if the node is open at a specific time
        # Expands the reservation table if the request depth exceeds the table's depth
        if timeDepth + self.currentDepth >= self.timeTracked:
            self.expandReservationTable(timeDepth + self.currentDepth)
        
        # If the agent is considering a "wait" move, where it does not move
        # print(targetNode)
        # print(sourceNode)
        if targetNode == sourceNode:
            # Have to check all edges leading to this node, and the future node
            edgeFree = True
            for node in self.reservationTable[timeDepth+self.currentDepth][sourceNode]:
                edgeFree = edgeFree and self.getEdgeState(timeDepth+self.currentDepth, sourceNode, node)
            nodeFree = self.getNodeState(timeDepth+self.currentDepth+1, sourceNode)
        else:
            edgeFree = self.getEdgeState(timeDepth + self.currentDepth, sourceNode, targetNode)
            nodeFree = self.getNodeState(timeDepth + self.currentDepth + 1, targetNode)
        if nodeFree and edgeFree:
            # print(f"{targetNode} in {timeDepth} from now ({timeDepth+self.currentDepth}) is accessible.")
            # Node is occupied and ineligible for use in pathfinding
            return True
        elif not nodeFree:
            # print(f"<<<{targetNode} in {timeDepth} from now ({timeDepth+self.currentDepth}) is NODE BLOCKED.")
            return False
        elif not edgeFree:
            # print(f"<<<{targetNode} in {timeDepth} from now ({timeDepth+self.currentDepth}) is EDGE BLOCKED")
            return False
        
    def handlePathPlanRequest(self, requestedNodeList):
        # Reserves nodes and edges for the found path, starting from currentDepth
        for depth, node in enumerate(requestedNodeList[1:]):
            # Reserve the edge at this time step
            self.reserveEdge(depth+self.currentDepth, requestedNodeList[depth], node)
            # Reserve the node at the next time step
            self.reserveNode(depth+self.currentDepth+1, node)

    def handlePathRelease(self, requestedNodeList):
        # Releases nodes and edges for the provided path, starting fromcurrentDepth
        for depth, node in enumerate(requestedNodeList[1:]):
            # Release the edge at this time step
            self.releaseEdge(depth+self.currentDepth, requestedNodeList[depth], node)
            # Release the node at the next time step
            self.releaseNode(depth+self.currentDepth+1, node)
            print(f"Released {node}")
            pp.pprint(self.reservationTable[depth+self.currentDepth+1].nodes(data=True))

    def createReservationTable(self):
        # Build the table for the depth
        self.reservationTable = {
            0: deepcopy(self.graphStructure),
        }

        # Preallocate nodes as being unreserved
        self.preallocNodes(0)
        self.preallocEdges(0)

        # Instantiate a counter that tracks the forward progression of time = depth of dict
        self.depthCounter = count()
        self.timeTracked = next(self.depthCounter)

    def reserveNode(self, timeStep, node):
        self.reservationTable[timeStep].nodes[node]["Reserved"] = False

    def reserveEdge(self, timeStep, sourceNode, targetNode):
        # If the agent's plan is to wait, then all neighboring edges need to be reserved
        if sourceNode == targetNode:
            for neighbor in self.reservationTable[timeStep][sourceNode]:
                self.reservationTable[timeStep][sourceNode][neighbor]["Reserved"] = False
        else:
            self.reservationTable[timeStep][sourceNode][targetNode]["Reserved"] = False

    def releaseNode(self, timeStep, node):
        self.reservationTable[timeStep].nodes[node]["Reserved"] = True

    def releaseEdge(self, timeStep, sourceNode, targetNode):
        self.reservationTable[timeStep][sourceNode][targetNode]["Reserved"] = True

    def getNodeState(self, timeStep, node):
        return self.reservationTable[timeStep].nodes[node]["Reserved"]

    def getEdgeState(self, timeStep, sourceNode, targetNode):
        return self.reservationTable[timeStep][sourceNode][targetNode]["Reserved"]

    def expandReservationTable(self, timeDepth):
        self.reservationTable[timeDepth+1] = deepcopy(self.graphStructure)
        self.preallocNodes(timeDepth+1)
        self.preallocEdges(timeDepth+1)
        self.timeTracked = next(self.depthCounter)

    def preallocNodes(self, timeDepth):
        nx.set_node_attributes(self.reservationTable[timeDepth], True, "Reserved")

    def preallocEdges(self, timeDepth):
        nx.set_edge_attributes(self.reservationTable[timeDepth], True, "Reserved")

    def initRRAstarPathfind(self, endNode, heuristicID):
        # Construct a dict of requested end nodes, with their RRA data stored for quick access
        if endNode not in self.RRAdata:
            self.RRAdata[endNode] = {
                "weight": 1, "gScore": {}, "fScore": {}, "openSet": [], "counter": count()
            }
        # If the heuristic hasn't been set yet, set it now
        if self.heuristicFunc is None:
            self.setHeuristic(heuristicID)

    def setHeuristic(self, heuristicID):
        # Define the heuristic based on the input
        # Heuristic accepts two nodes and calculates a "distance" estimate that must be admissible
        print(f"Setting heuristic: {heuristicID}")
        if heuristicID == "Dijkstra":
            def heuristic(u, v):
                # Dijkstra's always underestimates, making it admissible, but does nothing to speed up pathfinding
                return 0
            self.heuristicFunc = heuristic
        elif heuristicID == "Manhattan":
            def heuristic(u, v):
                # Manhattan/taxicab distance is the absolute value of the difference 
                uPos = self.mapGraphRef.nodes[u]['pos']
                vPos = self.mapGraphRef.nodes[v]['pos']
                heuristicDistance = abs(uPos['X']-vPos['X']) + abs(uPos['Y']-vPos['Y'])
                return heuristicDistance
            self.heuristicFunc = heuristic
        elif heuristicID == "Euclidean":
            def heuristic(u, v):
                # Euclidean/rectilinear/pythagoras distance is line length between two points
                uPos = self.mapGraphRef.nodes[u]['pos']
                vPos = self.mapGraphRef.nodes[v]['pos']
                heuristicDistance = sqrt((uPos['X']-vPos['X'])**2 + (uPos['Y']-vPos['Y'])**2)
                return heuristicDistance
            self.heuristicFunc = heuristic
        elif heuristicID == "Approx. Euclidean":
            def heuristic(u, v):
                # An approximation of euclidean distance
                uPos = self.mapGraphRef.nodes[u]['pos']
                vPos = self.mapGraphRef.nodes[v]['pos']
                delta_1 = abs(uPos['X']-vPos['X'])
                delta_2 = abs(uPos['Y']-vPos['Y'])
                b = max(delta_1, delta_2)
                a = min(delta_1, delta_2)
                heuristicDistance = b + 0.428 * a * a / b
                return heuristicDistance
            self.heuristicFunc = heuristic

    def calculateHeuristicDistance(self, sourceNode, targetNode, heuristicID):
        """
            Accepts the node of the agent as sourceNode
            Accepts the node of the goal node as targetNode
            Checks for the value already being in the dataset, and returns the hScore
            If it isn't, performs RRA* until the sourceNode is included
        """
        # Check for the existence of the targetNode in the data
        if targetNode not in self.RRAdata:
            self.initRRAstarPathfind(targetNode, heuristicID)
            # Set the initial search conditions
            nodeRRAdata = self.RRAdata[targetNode]
            heappush(nodeRRAdata["openSet"], (0, next(nodeRRAdata["counter"]), targetNode))
            nodeRRAdata["gScore"][targetNode] = 0
            nodeRRAdata["fScore"][targetNode] = self.heuristicFunc(targetNode, sourceNode)

        # print(self.RRAdata[targetNode])

        # Check if the sourceNode has been checked already
        if sourceNode in self.RRAdata[targetNode]["gScore"]:
            print(f"{sourceNode}->{targetNode} gScore is cached: {self.RRAdata[targetNode]['gScore'][sourceNode]}")
            return self.RRAdata[targetNode]["gScore"][sourceNode]
        
        # If not, then the node needs to be searched for via RRA* until its hScore is found
        self.RRAsearch(sourceNode, targetNode)
        print(self.RRAdata[targetNode]["gScore"][sourceNode])
        return self.RRAdata[targetNode]["gScore"][sourceNode]

    def RRAsearch(self, sourceNode, targetNode):
        nodeRRA = self.RRAdata[targetNode]
        # print(nodeRRA["openSet"])
        # print(type(nodeRRA["openSet"]))
        while nodeRRA["openSet"]:
            # Read the new node in the openSet to see if it matches the goal
            _, __, currentNode = min(nodeRRA["openSet"])
            # print(f"Currently checking node: {currentNode}")
            # print(currentNode)
            if currentNode == sourceNode:
                heappush(nodeRRA["openSet"], (_, __, currentNode))
                # The node has been found, and the search can end
                return True
            # Pop the next lowest fScore node for evaluation fo neighbors
            _, __, currentNode = heappop(nodeRRA["openSet"])
            # print(f"Node has neighbors:")
            for neighborNode in self.mapGraphRef.neighbors(currentNode):
                # print(f"\t{neighborNode}")1
                # Calculate the neighbors estimated gScore
                est_gScore = nodeRRA["gScore"][currentNode] + nodeRRA["weight"]
                # print(f"\tEst. gScore: {est_gScore}")
                # print(f"\tVs current stored: {nodeRRA['gScore'].get(neighborNode, inf)}")
                if est_gScore < nodeRRA["gScore"].get(neighborNode, inf):
                    # If the estimate is lower, a new best path to the node has been found
                    nodeRRA["gScore"][neighborNode] = est_gScore
                    # Calculate the fScore for this node
                    node_fScore = est_gScore + self.heuristicFunc(currentNode, sourceNode)
                    # print("\tCalculated new fScore: ")
                    # If this new node isn't already in the openSet, add it
                    # print( neighborNode not in nodeRRA["fScore"])
                    if neighborNode not in nodeRRA["fScore"]:
                        heappush(nodeRRA["openSet"], (node_fScore, next(nodeRRA["counter"]), neighborNode))
                    # Update the fScore
                    nodeRRA["fScore"][neighborNode] = node_fScore
            # print(f"Open set: {nodeRRA['openSet']}")
            # print(f"Closed set: {nodeRRA['gScore']}")
        raise nx.NetworkXNoPath(f"Node {targetNode} not reachable from {sourceNode}")
