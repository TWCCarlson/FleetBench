import networkx as nx
from heapq import heappop, heappush
from itertools import count
from numpy import inf
from numpy import sqrt
import pprint
pp = pprint.PrettyPrinter(indent=4)
import copy

class CAstarPathfinder:
    """
        Class which persists the state of pathfinding
        Should contain methods for advancing the search
    """
    def __init__(self, numID, mapCanvas, mapGraph, sourceNode, targetNode, config, pathManager):
        # Verify that the requested nodes exist in the graph first
        if not mapGraph.has_node(sourceNode) and not mapGraph.has_node(targetNode):
            msg = f"Either source {sourceNode} or target {targetNode} is not in graph."
            raise nx.NodeNotFound(msg)
        
        # Heuristic coefficient is limited, has to be greater than 1
        if config["heuristicCoefficient"] < 1:
            config["heuristicCoefficient"] = 1

        # If a pathfind operation can be attempted, save the inputs
        self.numID = numID
        self.sourceNode = sourceNode
        self.targetNode = targetNode
        self.heuristic = config["heuristic"]
        self.heuristicCoefficient = config["heuristicCoefficient"]
        self.collisionBehavior = config["agentCollisionsValue"]
        self.mapGraphRef = mapGraph
        self.mapCanvas = mapCanvas
        self.invalid = False
        self.pathManager = pathManager
        print(f"{self.numID}:{self.sourceNode}->{self.targetNode}")

        # Define the heuristic based on the input
        # Heuristic accepts two nodes and calculates a "distance" estimate that must be admissible
        if self.heuristic == "Dijkstra":
            def heuristic(u, v):
                # Dijkstra's always underestimates, making it admissible, but does nothing to speed up pathfinding
                return 0
            self.heuristicFunc = heuristic
        elif self.heuristic == "Manhattan":
            def heuristic(u, v):
                # Manhattan/taxicab distance is the absolute value of the difference 
                uPos = self.mapGraphRef.nodes[u]['pos']
                vPos = self.mapGraphRef.nodes[v]['pos']
                heuristicDistance = abs(uPos['X']-vPos['X']) + abs(uPos['Y']-vPos['Y'])
                return heuristicDistance
            self.heuristicFunc = heuristic
        elif self.heuristic == "Euclidean":
            def heuristic(u, v):
                # Euclidean/rectilinear/pythagoras distance is line length between two points
                uPos = self.mapGraphRef.nodes[u]['pos']
                vPos = self.mapGraphRef.nodes[v]['pos']
                heuristicDistance = sqrt((uPos['X']-vPos['X'])**2 + (uPos['Y']-vPos['Y'])**2)
                return heuristicDistance
            self.heuristicFunc = heuristic
        elif self.heuristic == "Approx. Euclidean":
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
        
        # All edges in the graph should have a weight of "1"
        # Therefore there is no need to calculate the weights, as neighborliness is assured by .items()
        self.weight = 1

        # Define gScore, fScore, and parent node dicts
        self.gScore = {} # gScore is the distance from source to current node
        self.fScore = {} # fScore is the distance from source to target through current node
        self.cameFrom = {} # cameFrom holds the optimal previous node on the path to the current node

        # The openset, populated with the first node
        # The heap queue pulls the smallest item from the heap
        # The first element in the format is the fScore, minimizing this is an objective
        # The second element is a counter, used to break ties in the fScore
        self.counter = count()
        self.openSet = []

        # Set the start of the heap up
        # Initialize the starting node into the queue, alongside its appropriate maps
        heappush(self.openSet, (0, next(self.counter), sourceNode, 0))
        self.gScore[(sourceNode, 0)] = 0
        self.fScore[(sourceNode, 0)] = self.heuristicFunc(sourceNode, targetNode)

        # Data used for tracking pathfinder performance
        self.searchOps = count()

        # Stored ideal path, which agent should follow unless not possible
        self.plannedPath = []

        # Clear the current pathfinding markers
        # self.mapCanvas.requestRender("highlight", "clear", {})
        # self.mapCanvas.requestRender("canvasLine", "clear", {})
        # self.mapCanvas.requestRender("text", "clear", {})
        # self.mapCanvas.handleRenderQueue()

        # Mark the target
        self.mapCanvas.requestRender("highlight", "new", {"targetNodeID": self.targetNode, "highlightType": "pathfindHighlight", "multi": True, "color": "cyan"})

    def __copy__(self):
        # Used to export data about the pathfinder's current state for reinit
        pathfinderData = {
            "sourceNode": self.sourceNode,
            "targetNode": self.targetNode,
            # "heuristic": self.heuristic,
            # "heuristicCoefficient": self.heuristicCoefficient,
            # "collisionBehavior": self.collisionBehavior,
            # "weight": self.weight,
            # "gScore": copy.deepcopy(self.gScore),
            # "fScore": copy.deepcopy(self.fScore),
            # "cameFrom": copy.deepcopy(self.cameFrom),
            "counter": next(self.counter),
            "searchOps": next(self.searchOps),
            "plannedPath": copy.deepcopy(self.plannedPath)
        }
        return pathfinderData
    
    def __load__(self, pathfinderData):
        # All fields required for this to work properly
        self.sourceNode = pathfinderData["sourceNode"]
        self.targetNode = pathfinderData["targetNode"]
        # self.heuristic = pathfinderData["heuristic"]
        # self.heuristicCoefficient = pathfinderData["heuristicCoefficient"]
        # self.collisionBehavior = pathfinderData["collisionBehavior"]
        # self.weight = copy.deepcopy(pathfinderData["weight"])
        # self.gScore = copy.deepcopy(pathfinderData["gScore"])
        # self.fScore = copy.deepcopy(pathfinderData["fScore"])
        # self.cameFrom = pathfinderData["cameFrom"]
        self.counter = count(start=pathfinderData["counter"]-1, step=1)
        self.searchOps = count(start=pathfinderData["searchOps"]-1, step=1)
        self.plannedPath = copy.deepcopy(pathfinderData["plannedPath"])

    def __reset__(self):
        # Reset the pathfinder to its default state, effectively restarting the search
        self.gScore = {} # gScore is the distance from source to current node
        self.fScore = {} # fScore is the distance from source to target through current node
        self.cameFrom = {} # cameFrom holds the optimal previous node on the path to the current node

        # The openset, populated with the first node
        # The heap queue pulls the smallest item from the heap
        # The first element in the format is the fScore, minimizing this is an objective
        # The second element is a counter, used to break ties in the fScore
        # Third element is the node ID
        # Last element is the time depth of the search, incremented on each neighbor exploration
        self.counter = count()
        self.openSet = []
        heappush(self.openSet, (0, next(self.counter), self.sourceNode, 0))
        self.gScore[(self.sourceNode, 0)] = 0
        self.fScore[(self.sourceNode, 0)] = self.heuristicFunc(self.sourceNode, self.targetNode)

        # Data used for tracking pathfinder performance
        self.searchOps = count()

        # Stored ideal path, which agent should follow unless not possible
        self.plannedPath = []

        # Further, flag this pathfinder as invalid
        self.invalid = True

    def searchStep(self):
        # Seek the shortest path between the targetNode and agent's currentNode
        # Account for obstacles (other agents)
        # Recursively work through the queue 
        if self.openSet:
            _, __, currentNode, timeDepth = heappop(self.openSet)
            if currentNode == self.targetNode:
                # Return successfully, with the reconstructed path if the currentNode is the targetNode
                path = [currentNode]
                parentNodeTime = self.cameFrom.get((currentNode, timeDepth), None)
                while parentNodeTime is not None:
                    path.append(parentNodeTime[0])
                    parentNodeTime = self.cameFrom.get(parentNodeTime, None)
                # Reverse the path to get the route from source to target
                path.reverse()
                self.plannedPath = path
                # print(f"Pathfinder found path: {self.plannedPath}")
                # Update reservation table
                self.pathManager.handlePathPlanRequest(path, self.numID)
                return True
            
            # Neighbor nodes needs to be augmented with the same node, but one time step removed
            neighborNodes = list(self.mapGraphRef.neighbors(currentNode)) + [currentNode]

            for neighborNode in neighborNodes:
                if not self.pathManager.evaluateNodeEligibility(timeDepth, neighborNode, currentNode, self.numID) and self.collisionBehavior == "Respected":
                    # print(f"<<<Node {neighborNode} was blocked")
                    continue
                est_gScore = self.gScore[(currentNode, timeDepth)] + self.weight
                # If this estimated gScore for the neighbor is less than the currently mapped one
                if est_gScore < self.gScore.get((neighborNode, timeDepth+1), inf):
                    # Then a new best path has been found to reach the neighbor node
                    self.cameFrom[(neighborNode, timeDepth+1)] = (currentNode, timeDepth)
                    # Record its new gScore
                    self.gScore[(neighborNode, timeDepth+1)] = est_gScore       
                    # Calculate the fScore for the neighbor node
                    node_fScore = est_gScore + self.heuristicFunc(currentNode, self.targetNode) * self.heuristicCoefficient
                    # If the node isn't already in the openSet, add it
                    if neighborNode not in self.fScore:
                        heappush(self.openSet, (node_fScore, next(self.counter), neighborNode, timeDepth+1))
                    # Update the fScore of the neighbor node
                    self.fScore[(neighborNode, timeDepth+1)] = node_fScore
            return False
        else:
            return "wait"
            # raise nx.NetworkXNoPath(f"Node {self.targetNode} not reachable from {self.sourceNode}")
        
    def searchStepRender(self):
        # Render the process of searching
        # Seek the shortest path between the targetNode and agent's currentNode
        # Account for obstacles (other agents)
        # Recursively work through the queue 
        # Highlight the target node
        if self.openSet:
            _, __, currentNode, timeDepth = heappop(self.openSet)
            # Indicate tile is explored
            self.mapCanvas.requestRender("highlight", "delete", {"highlightType": "openSet"})
            self.mapCanvas.requestRender("highlight", "new", {"targetNodeID": currentNode, "highlightType": "pathfindHighlight", "multi": True})
            if currentNode == self.targetNode:
                # Return successfully, with the reconstructed path if the currentNode is the targetNode
                path = [currentNode]
                parentNodeTime = self.cameFrom.get((currentNode, timeDepth), None)
                while parentNodeTime is not None:
                    path.append(parentNodeTime[0])
                    parentNodeTime = self.cameFrom.get((parentNodeTime), None)
                # Reverse the path to get the route from source to target
                path.reverse()
                self.plannedPath = path
                # print(f"Pathfinder found path: {self.plannedPath}")
                # print(path)
                self.mapCanvas.requestRender("canvasLine", "new", {"nodePath": self.plannedPath, "lineType": "pathfind"})
                self.pathManager.handlePathPlanRequest(path, self.numID)
                # self.mapCanvas.handleRenderQueue()
                return True
            
            # Neighbor nodes needs to be augmented with the same node, but one time step removed
            neighborNodes = list(self.mapGraphRef.neighbors(currentNode)) + [currentNode]
            # print("!!! NEW NODE SET !!!")
            for neighborNode in neighborNodes:
                # Cooperative A* uses a reservation table to determine neighbor eligibility
                # "Temporal adjacency"; True indicates eligibility
                # print("==========================================")
                # print(f">>>Evaluate {currentNode}->{neighborNode}: {timeDepth}")
                if not self.pathManager.evaluateNodeEligibility(timeDepth, neighborNode, currentNode, self.numID) and self.collisionBehavior == "Respected":
                    # print(f"<<<Node {neighborNode} was blocked")
                    self.mapCanvas.requestRender("highlight", "new", {"targetNodeID": neighborNode, "highlightType": "agentHighlight", "multi": True})
                    continue

                self.mapCanvas.requestRender("highlight", "new", {"targetNodeID": neighborNode, "highlightType": "openSet", "multi": True, "color": "yellow", "highlightTags": ["openSet"]})
                est_gScore = self.gScore[(currentNode, timeDepth)] + self.weight
                # If this estimated gScore for the neighbor is less than the currently mapped one
                if est_gScore < self.gScore.get((neighborNode, timeDepth+1), inf):
                    # Then a new best path has been found to reach the neighbor node
                    self.cameFrom[(neighborNode, timeDepth+1)] = (currentNode, timeDepth)
                    # Record its new gScore
                    self.gScore[(neighborNode, timeDepth+1)] = est_gScore
                    # Calculate nodes estimated distance from the goal
                    hScore = self.heuristicFunc(currentNode, self.targetNode) * self.heuristicCoefficient
                    # Calculate the fScore for the neighbor node
                    node_fScore = est_gScore + hScore
                    # If the node isn't already in the openSet, add it
                    if neighborNode not in self.fScore:
                        heappush(self.openSet, (node_fScore, next(self.counter), neighborNode, timeDepth+1))
                    # Update the fScore of the neighbor node
                    self.fScore[(neighborNode, timeDepth+1)] = node_fScore
                    
                    # Display tile scores
                    self.mapCanvas.requestRender("text", "new", {"position": neighborNode, "text": f" g{est_gScore}", "textType": "pathfind", "anchor": "nw"})
                    self.mapCanvas.requestRender("text", "new", {"position": neighborNode, "text": f"h{round(hScore)} ", "textType": "pathfind", "anchor": "ne"})
                    self.mapCanvas.requestRender("text", "new", {"position": neighborNode, "text": f"f{round(node_fScore)} ", "textType": "pathfind", "anchor": "se"})
                    self.mapCanvas.requestRender("text", "new", {"position": neighborNode, "text": f" T{timeDepth+1}", "textType": "pathfind", "anchor": "sw"})
                    self.mapCanvas.requestRender("highlight", "new", {"targetNodeID": neighborNode, "highlightType": "pathfindHighlight", "multi": True})

            self.mapCanvas.handleRenderQueue()
            return False
        else:
            pp.pprint(self.openSet)
            return "wait"
            # raise nx.NetworkXNoPath(f"Node {self.targetNode} not reachable from {self.sourceNode}")