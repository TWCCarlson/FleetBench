from pprint import PrettyPrinter
import tkinter as tk
from tkinter import filedialog
import json
import networkx as nx
from tsmpy import TSM
import matplotlib.pyplot as plt

import pprint
pp = pprint.PrettyPrinter(indent=4)

class mapDataClass:
    """
        Class storing the graph on which the warehouse is based
    """
    def __init__(self, parent):
        self.parent = parent
        print("Map Data Class gen")
        # Create the graph object
        self.mapGraph = nx.Graph()
        self.mapLoadedBool = False

    def buildReferences(self):
        self.mainView = self.parent.mainView
        self.appearanceValues = self.parent.appearance

    def ingestMapFromJSON(self):
        # Choose map data file to load
        path = tk.filedialog.askopenfile(title="Load Map JSON", filetypes = [("Text", ".txt")])
        if path != None:
            mapData = json.load(path)
            # pp.pprint(mapData)
            self.loadMapToNetworkX(mapData)
        
    def loadMapToNetworkX(self, mapData):
        pp.pprint(mapData)
        self.mapGraph.clear()
        for node in mapData:
            if 'mapDimensions' in node:
                # This json entry is only for setting max dims
                self.dimensionX = node['mapDimensions']['Xdim']-1
                self.dimensionY = node['mapDimensions']['Ydim']-1
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

            # Add nodes to the graph with name
            self.mapGraph.add_node(nodeName, pos=nodePosition, type=nodeType, edgeDirs=nodeEdges)
        
        # print(self.mapGraph.nodes.data())
        # Add edges based on the nodelist
        for node in self.mapGraph.nodes.data():
            # Generate nodes it should be connected to
            # print(node[0])
            nodeData = node[1]
            # Take the base position
            nodePosition = (nodeData['pos']['X'], nodeData['pos']['Y'])
            # Calculate candidates based on edges
            # print(node[0])
            # print(nodeData)

            if nodeData['edgeDirs']['N'] == 1:
                candidateN = str((nodePosition[0], nodePosition[1]-1))
                # print(candidateN)
                # Check if the candidate node exists
                if candidateN in self.mapGraph.nodes:
                    # Check if the candidate node has an edge in this direction
                    if self.mapGraph.nodes.data()[candidateN]['edgeDirs']['S'] == 1:
                        # print("exists:" + str(candidateN) + "->" + str(node[0]))
                        self.mapGraph.add_edge(node[0], candidateN)

            if nodeData['edgeDirs']['W'] == 1:
                candidateW = str((nodePosition[0]-1, nodePosition[1]))
                # Check if the candidate node exists
                if candidateW in self.mapGraph.nodes:
                    # Check if the candidate node has an edge in this direction
                    if self.mapGraph.nodes.data()[candidateW]['edgeDirs']['E'] == 1:
                        # print("exists:" + str(candidateW) + "->" + str(node[0]))
                        self.mapGraph.add_edge(node[0], candidateW)

            if nodeData['edgeDirs']['S'] == 1:
                candidateS = str((nodePosition[0], nodePosition[1]+1))
                # Check if the candidate node exists
                if candidateS in self.mapGraph.nodes:
                    # Check if the candidate node has an edge in this direction
                    if self.mapGraph.nodes.data()[candidateS]['edgeDirs']['N'] == 1:
                        # print("exists:" + str(candidateS) + "->" + str(node[0]))
                        self.mapGraph.add_edge(node[0], candidateS)

            if nodeData['edgeDirs']['E'] == 1:
                candidateE = str((nodePosition[0]+1, nodePosition[1]))
                # Check if the candidate node exists
                if candidateE in self.mapGraph.nodes:
                    # Check if the candidate node has an edge in this direction
                    if self.mapGraph.nodes.data()[candidateE]['edgeDirs']['W'] == 1:
                        # print("exists:" + str(candidateE) + "->" + str(node[0]))
                        self.mapGraph.add_edge(node[0], candidateE)
        
        # Update mainView canvas size
        canvasWidth = (self.dimensionX+1) * self.appearanceValues.canvasTileSize
        canvasHeight = (self.dimensionY+1) * self.appearanceValues.canvasTileSize
        self.mainView.mainCanvas["width"] = canvasWidth
        self.mainView.mainCanvas["height"] = canvasHeight
        self.mainView.mainCanvas["scrollregion"] = (0, 0, canvasWidth, canvasHeight)

        try:
            pos = {node: eval(node) for node in self.mapGraph}
            # tsm = TSM(self.mapGraph, pos)
            # tsm.display()
            # plt.subplot(111)
            # nx.draw(self.mapGraph, with_labels=True, font_weight='bold')
            # plt.show()
            self.mainView.mainCanvas.renderGraphState()
        except:
            tk.messagebox.showwarning(title="Failed to load map", message="Map's graph is invalid. Verify there are no unconnected nodes...")
            # plt.subplot(111)
            # nx.draw(self.mapGraph, with_labels=True, font_weight='bold')
            # plt.show()
            self.mainView.mainCanvas.renderGraphState()

        # Enable the rest of the program options to work
        self.mapLoadedBool = True
        self.parent.toolBar.enableAgentCreation()
        self.parent.toolBar.enableTaskCreation()
        
        # for node in self.mapGraph:
        #     pp.pprint(eval(node))

    def updateAgentLocations(self, agentList, ):
        print("update Agent locations in graph")

        # Remove all agents from the graph
        for node in self.mapGraph.nodes(data=True):
            if 'agent' in self.mapGraph.nodes.data()[node[0]]:
                del self.mapGraph.nodes.data()[node[0]]['agent']
            else:
                # print(str(node) + " does not contain an agent" )
                pass

        # Insert agents from the agent list back into the graph
        for agent in agentList:
            agentPosition = agentList[agent].position
            targetNode = f"({agentPosition[0]}, {agentPosition[1]})"
            self.mapGraph.nodes[targetNode]['agent'] = agentList[agent]

        # for node in self.mapGraph.nodes(data=True):
        #     # print("Agent in node")
        #     print(node[0])
        #     try:
        #         print(self.mapGraph.nodes.data()[node[0]]['agent'])
        #     except:
        #         print("No agent")

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
            # nodeData = node[1]
            # pp.pprint(nodeData)
        pp.pprint(dataPackage)
        return dataPackage