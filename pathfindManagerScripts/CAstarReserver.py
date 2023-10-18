import networkx as nx
import numpy as np
import pprint
pp = pprint.PrettyPrinter(indent=4)
import sys
from copy import deepcopy
from itertools import count

class CAstarReserver:
    """
        Class which maintains a "reservation table for the cooperative A* technique
    """
    def __init__(self, mapGraph):
        # Store the base graph
        self.mapGraphRef = mapGraph
    
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

    def evaluateNodeEligibility(self, timeDepth, targetNode, sourceNode, agentID):
        # Verifies if the node is open at a specific time
        # Expands the reservation table if the request depth exceeds the table's depth
        if timeDepth + self.currentDepth >= self.timeTracked:
            self.expandReservationTable(timeDepth + self.currentDepth)
        
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
        
    def handlePathPlanRequest(self, requestedNodeList, agentID):
        # Reserves nodes and edges for the found path, starting from currentDepth
        for depth, node in enumerate(requestedNodeList[1:]):
            # Reserve the edge at this time step
            self.reserveEdge(depth+self.currentDepth, requestedNodeList[depth], node, agentID)
            # Reserve the node at the next time step
            self.reserveNode(depth+self.currentDepth+1, node, agentID)

    def handlePathRelease(self, requestedNodeList, agentID):
        # Releases nodes and edges for the provided path, starting fromcurrentDepth
        for depth, node in enumerate(requestedNodeList[1:]):
            # Release the edge at this time step
            self.releaseEdge(depth+self.currentDepth, requestedNodeList[depth], node, agentID)
            # Release the node at the next time step
            self.releaseNode(depth+self.currentDepth+1, node, agentID)
            # print(f"Released {node}")
            # pp.pprint(self.reservationTable[depth+self.currentDepth+1].nodes(data=True))

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

    def reserveNode(self, timeStep, node, agentID):
        self.reservationTable[timeStep].nodes[node]["Reserved"] = str(agentID)

    def reserveEdge(self, timeStep, sourceNode, targetNode, agentID):
        # If the agent's plan is to wait, then all neighboring edges need to be reserved
        if sourceNode == targetNode:
            for neighbor in self.reservationTable[timeStep][sourceNode]:
                self.reservationTable[timeStep][sourceNode][neighbor]["Reserved"] = str(agentID)
        else:
            self.reservationTable[timeStep][sourceNode][targetNode]["Reserved"] = str(agentID)

    def releaseNode(self, timeStep, node, agentID):
        if self.reservationTable[timeStep].nodes[node]["Reserved"] == agentID:
            self.reservationTable[timeStep].nodes[node]["Reserved"] = False

    def releaseEdge(self, timeStep, sourceNode, targetNode, agentID):
        if self.reservationTable[timeStep][sourceNode][targetNode]["Reserved"] == agentID:
            self.reservationTable[timeStep][sourceNode][targetNode]["Reserved"] = False

    def getNodeState(self, timeStep, node, agentID):
        reserver = self.reservationTable[timeStep].nodes[node]["Reserved"]
        # print(f"Node: {self.reservationTable[timeStep].nodes[node]['Reserved']}; {bool(self.reservationTable[timeStep].nodes[node]['Reserved'])}")
        if reserver == str(agentID):
            # print("Node reserved by self.")
            return False
        elif reserver == False:
            return False
        else:
            # print("Node reserved by another.")
            return True

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

    def expandReservationTable(self, timeDepth):
        self.reservationTable[timeDepth+1] = deepcopy(self.graphStructure)
        self.preallocNodes(timeDepth+1)
        self.preallocEdges(timeDepth+1)
        self.timeTracked = next(self.depthCounter)

    def preallocNodes(self, timeDepth):
        nx.set_node_attributes(self.reservationTable[timeDepth], False, "Reserved")

    def preallocEdges(self, timeDepth):
        nx.set_edge_attributes(self.reservationTable[timeDepth], False, "Reserved")
