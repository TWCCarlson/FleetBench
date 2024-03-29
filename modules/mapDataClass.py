import tkinter as tk
from tkinter import filedialog
import json
import networkx as nx
from tsmpy import TSM
import matplotlib.pyplot as plt
import logging
import pprint
pp = pprint.PrettyPrinter(indent=4)

from timeit import default_timer as timer

class mapDataClass:
    """
        Class storing the graph on which the warehouse is based
    """
    def __init__(self, parent):
        logging.debug("Map Data class initializing . . .")
        self.parent = parent
        # Create the graph object
        self.mapGraph = nx.Graph()
        self.mapLoadedBool = False
        logging.debug(f"Map data class graph object instantiated: {self.mapGraph}")
        logging.info("No map is loaded.")
        logging.info("Map Data class finished initializing.")

    def buildReferences(self):
        self.mainView = self.parent.mainView
        self.appearanceValues = self.parent.appearance
        logging.debug("References for 'mapData' are built.")

    def ingestMapFromJSON(self):
        # Choose map data file to load
        logging.debug("Requesting user to select a map file for ingest . . .")
        path = tk.filedialog.askopenfile(title="Load Map JSON", filetypes = [("Text", ".txt")])
        if path != None:
            logging.debug(f"User chose to ingest file: {path}")
            mapData = json.load(path)
            logging.debug(f"With data:")
            logging.debug(f"{mapData}")
            # pp.pprint(mapData)
            self.loadMapToNetworkX(mapData)
        
    def loadMapToNetworkX(self, mapData):
        logging.debug("Resetting old mapGraph to make space for new mapData.")
        self.mapGraph.clear()
        logging.debug(f"Attempting to load mapData into the mapGraph . . .")
        for node in mapData:
            if 'mapDimensions' in node:
                # This json entry is only for setting max dims
                self.dimensionX = node['mapDimensions']['Xdim']
                self.dimensionY = node['mapDimensions']['Ydim']
                self.mainView.mainCanvas.setCanvasDimensions(self.dimensionX, self.dimensionY)
                logging.debug(f"New mapGraph dimensions: X={self.dimensionX}, Y={self.dimensionY}")
                continue
            
            # pp.pprint(node)
            # Create the node name from its position for ease of reference
            # nodePositionList.append(node['nodePosition'])
            # nodeTypeList.append(node['nodeType'])
            # nodeEdgeList.append(node['nodeEdges'])
            nodeName = "(" + str(node['nodePosition']['X']) + ", " + str(node['nodePosition']['Y']) + ")"
            nodePosition = node['nodePosition']
            nodeType = node['nodeType']
            nodeEdges = node['nodeEdges']

            if nodeType == "void":
                # Skip this node, it doesn't really exist
                continue

            logging.debug(f"Add node '{nodeName}':{node}")
            # Add nodes to the graph with name
            self.mapGraph.add_node(nodeName, pos=nodePosition, type=nodeType, edgeDirs=nodeEdges)
        logging.info("New mapData nodes successfully loaded to mapGraph.")
        
        # print(self.mapGraph.nodes.data())
        # Add edges based on the nodelist
        logging.debug("Loading edges to nodes in mapGraph . . .")
        for node in self.mapGraph.nodes.data():
            # Generate nodes it should be connected to
            logging.debug(f"Checking for nodes connected to node: {node}")
            # print(node[0])
            nodeData = node[1]
            # Take the base position
            nodePosition = (nodeData['pos']['X'], nodeData['pos']['Y'])
            # Calculate candidates based on edges
            # print(node[0])
            # print(nodeData)

            logging.debug("Connected to:")
            if nodeData['edgeDirs']['N'] == 1:
                candidateN = str((nodePosition[0], nodePosition[1]-1))
                # print(candidateN)
                # Check if the candidate node exists
                if candidateN in self.mapGraph.nodes:
                    # Check if the candidate node has an edge in this direction
                    if self.mapGraph.nodes.data()[candidateN]['edgeDirs']['S'] == 1:
                        # print("exists:" + str(candidateN) + "->" + str(node[0]))
                        self.mapGraph.add_edge(node[0], candidateN)
                        logging.debug(f". . . . .  N: {candidateN}, edge connection added.")

            if nodeData['edgeDirs']['W'] == 1:
                candidateW = str((nodePosition[0]-1, nodePosition[1]))
                # Check if the candidate node exists
                if candidateW in self.mapGraph.nodes:
                    # Check if the candidate node has an edge in this direction
                    if self.mapGraph.nodes.data()[candidateW]['edgeDirs']['E'] == 1:
                        # print("exists:" + str(candidateW) + "->" + str(node[0]))
                        self.mapGraph.add_edge(node[0], candidateW)
                        logging.debug(f". . . . .  W: {candidateW}, edge connection added.")

            if nodeData['edgeDirs']['S'] == 1:
                candidateS = str((nodePosition[0], nodePosition[1]+1))
                # Check if the candidate node exists
                if candidateS in self.mapGraph.nodes:
                    # Check if the candidate node has an edge in this direction
                    if self.mapGraph.nodes.data()[candidateS]['edgeDirs']['N'] == 1:
                        # print("exists:" + str(candidateS) + "->" + str(node[0]))
                        self.mapGraph.add_edge(node[0], candidateS)
                        logging.debug(f". . . . .  S: {candidateS}, edge connection added.")

            if nodeData['edgeDirs']['E'] == 1:
                candidateE = str((nodePosition[0]+1, nodePosition[1]))
                # Check if the candidate node exists
                if candidateE in self.mapGraph.nodes:
                    # Check if the candidate node has an edge in this direction
                    if self.mapGraph.nodes.data()[candidateE]['edgeDirs']['W'] == 1:
                        # print("exists:" + str(candidateE) + "->" + str(node[0]))
                        self.mapGraph.add_edge(node[0], candidateE)
                        logging.debug(f". . . . .  E: {candidateE}, edge connection added.")
        logging.info("New mapData edges loaded to mapGraph.")

        # Enable the rest of the program options to work
        self.mapLoadedBool = True
        logging.debug("Map is now loaded. Enabling session interfaces . . .")
        self.parent.toolBar.enableAgentCreation()
        logging.debug("Agent creation is now enabled.")
        self.parent.toolBar.enableTaskCreation()
        logging.debug("Task creation is now enabled.")
        self.parent.contextView.enableSimulationConfiguration()
        logging.info("New mapData successfully ingested to new mapGraph.")

        self.pushDataToCanvas()
        self.parent.agentManager.pushDataToCanvas()
        self.parent.mainView.mainCanvas.delete("all")
        self.parent.mainView.mainCanvas.renderGraphState()

    def pushDataToCanvas(self):
        print("pushing to canvas")
        self.mainView.mainCanvas.ingestGraphData(self.mapGraph)

    def updateAgentLocations(self, agentList, ):
        logging.debug("Updating agent locations in the mapGraph . . .")

        # Remove all agents from the graph
        for node in self.mapGraph.nodes(data=True):
            if 'agent' in self.mapGraph.nodes.data()[node[0]]:
                logging.debug(f"Removed agent '{self.mapGraph.nodes.data()[node[0]]['agent'].ID}:{self.mapGraph.nodes.data()[node[0]]['agent'].numID}' from '{node[0]}'.")
                del self.mapGraph.nodes.data()[node[0]]['agent']
            else:
                # print(str(node) + " does not contain an agent" )
                pass

        # Insert agents from the agent list back into the graph
        for agent in agentList:
            agentPosition = agentList[agent].position
            targetNode = f"({agentPosition[0]}, {agentPosition[1]})"
            self.mapGraph.nodes[targetNode]['agent'] = agentList[agent]
            logging.debug(f"Inserted agent '{agentList[agent].ID}:{agent}' into mapGraph node '{targetNode}'.")

        logging.info("Agent data in mapGraph updated.")

    def packageMapData(self):
        """ 
            Package reconstruction data for replicating the current state of the graph
            This means the data needed to create each node, edge, and edge connection needs to be available
                - Nodes: '(0, 0)': { ...
                - Edges: ('(0, 1)', '(0, 2)', {}), ...
                - pos: 'pos': {'X': 0, 'Y': 0}
                - type: 'edge'/'charge'/'pickup'/'deposit'/'rest'
                - edgeDirs: 'edgeDirs': {'N': 1, 'W': 1, 'S': 1, 'E': 1}
        """
        logging.debug("Packaging mapData . . .")
        dataPackage = []
        mapDimData = {
            "mapDimensions": {
                "Xdim": self.dimensionX+1,
                "Ydim": self.dimensionY+1
            }
        }
        dataPackage.append(mapDimData)

        for node in self.mapGraph.nodes(data=True):
            # pp.pprint(node)
            nodeEdgeData = node[1]["edgeDirs"]
            nodePos = node[1]["pos"]
            nodeType = node[1]["type"]
            # Ignore task and data objects, can't be pickled, let them be repopulated independently
            nodeData = {
                "nodeEdges": nodeEdgeData,
                "nodePosition": nodePos,
                "nodeType": nodeType
            }
            dataPackage.append(nodeData)
            logging.debug(f"Adding {node} to data package:")
            # nodeData = node[1]
            # pp.pprint(nodeData)
        # pp.pprint(dataPackage)
        logging.info("Packaged all mapData.")
        return dataPackage
    
    def generateNodeListsByType(self):
        # Empty lists to be filled
        self.listOfEdgeNodes = []
        self.listOfPickupNodes = []
        self.listOfDropoffNodes = []
        self.listOfRestNodes = []
        self.listOfChargeNodes = []

        # Dict pairing node types with respective node lists
        dictOfTypesLists = {
            'edge': self.listOfEdgeNodes,
            'pickup': self.listOfPickupNodes,
            'deposit': self.listOfDropoffNodes,
            'rest': self.listOfRestNodes,
            'charge': self.listOfChargeNodes,
            'void': []
        }

        # Iterate through the list of nodes, sorting them by type using the dict
        for node in self.mapGraph.nodes(data=True):
            dictOfTypesLists[node[1]['type']].append(node[0])

        # Return a dict of the lists
        return dictOfTypesLists

    def generateAllTaskShortestPaths(self, pickupNodeList, depositNodeList):
        # start = timer()
        pathsDict = {}
        # dictionary = nx.all_pairs_shortest_path(self.mapGraph)
        for pickupNode in pickupNodeList:
            depositDict = {}
            for depositNode in depositNodeList:
                depositDict[depositNode] = nx.shortest_path(self.mapGraph, pickupNode, depositNode)
            pathsDict[pickupNode] = depositDict
        # stop = timer()
        # stuff = [x for x in dictionary]
        # timed = stop-start
        # pp.pprint(stuff)
        # print(pathsDict)
        # print(timed)
        return pathsDict