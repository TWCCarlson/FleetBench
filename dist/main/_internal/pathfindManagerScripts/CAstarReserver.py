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
            print(f"{targetNode} in {timeDepth} from now ({timeDepth+self.currentDepth}) is accessible.")
            # Node is occupied and ineligible for use in pathfinding
            return True
        elif nodeReserved:
            print(f"<<<{targetNode} in {timeDepth} from now ({timeDepth+self.currentDepth}) is NODE BLOCKED.")
            return False
        elif edgeReserved:
            print(f"<<<{targetNode} in {timeDepth} from now ({timeDepth+self.currentDepth}) is EDGE BLOCKED")
            return False
        
    def evaluateNodeOverwritability(self, timeDepth, targetNode, sourceNode, agentID, agentPriority):
        # print(f"Checking if its possible to overwrite {targetNode}...")
        # Verifies if the node is overwritable at a specific time
        # Expands the reservation table if the request depth exceeds the table's depth
        if timeDepth + self.currentDepth >= self.timeTracked:
            self.expandReservationTable(timeDepth + self.currentDepth)

        edgeReserver = self.getEdgeReserver(timeDepth + self.currentDepth, sourceNode, targetNode)
        if edgeReserver is False:
            # Its not even reserved
            edgeOverwritable = True
        else:
            # It is reserved, so compare priorities
            edgeOverwritable = (agentPriority.index(eval(edgeReserver)) >= agentPriority.index(agentID))

        nodeReserver = self.getNodeReserver(timeDepth+self.currentDepth+1, targetNode)
        if nodeReserver is False:
            # Its not even reserved
            nodeOverwritable = True
        else:
            nodeOverwritable = (agentPriority.index(eval(nodeReserver)) >= agentPriority.index(agentID))
        
        # print(f"Agent priority: {agentPriority}, for {agentID} vs. {edgeReserver}/{nodeReserver}")
        # print(f"Priority Positions: {agentPriority.index(agentID)} vs. {agentPriority.index(edgeReserver)}{agentPriority.index(nodeReserver)}")
        # print(f"Edge overwrite: {edgeReserver}:{edgeOverwritable}, Node overwrite: {nodeReserver}:{nodeOverwritable}")
        if edgeOverwritable and nodeOverwritable:
            # print(f"<<<{agentID} can overwrite {edgeReserver}:edge and {nodeReserver}:node")
            return (True, edgeReserver, nodeReserver)
        elif edgeOverwritable:
            # print(f"<<<Unable to overwrite {nodeReserver}:{targetNode} in {timeDepth} from now ({timeDepth+self.currentDepth}): NODE BLOCKED")
            return False
        elif nodeOverwritable:
            # print(f"<<<Unable to overwrite {edgeReserver}:{targetNode}{sourceNode} in {timeDepth} from now ({timeDepth+self.currentDepth}): EDGE BLOCKED")
            return False
        
    def handlePathPlanRequest(self, requestedNodeList, agentID):
        # Reserves nodes and edges for the found path, starting from currentDepth
        for depth, node in enumerate(requestedNodeList[1:]):
            # Reserve the edge at this time step
            self.reserveEdge(depth+self.currentDepth, requestedNodeList[depth], node, agentID)
            # Reserve the node at the next time step
            self.reserveNode(depth+self.currentDepth+1, node, agentID)

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
        reserver = self.reservationTable[timeStep].nodes[node]["Reserved"]
        # print(f"Node: {self.reservationTable[timeStep].nodes[node]['Reserved']}; {bool(self.reservationTable[timeStep].nodes[node]['Reserved'])}")
        if reserver == str(agentID):
            print("Node reserved by self.")
            return False
        elif reserver == False:
            return False
        else:
            print(f"Node reserved by another: {reserver}")
            return True
        
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
