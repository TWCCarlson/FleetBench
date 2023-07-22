import networkx as nx
import logging
import pprint
pp = pprint.PrettyPrinter(indent=4)

class simGraphManager:
    def __init__(self, parent):
        self.parent = parent

        # Data structures
        self.simMapGraph = nx.Graph()

        ### Quick references
        # Reference to the canvas used to draw the map in the simulation window:
        self.simMapCanvas = self.parent.parent.simulationWindow.simMainView.simCanvas
        
        # Retrieve initial graph state from the session edit window
        self.retrieveInitialSimState()
        logging.debug("Class 'simGraphManager' initialized.")

    def retrieveInitialSimState(self):
        # Extract the data from the session edit window
        dataPackage = self.parent.parent.parent.mapData.packageMapData()

        # Process the data and load it into networkX
        for node in dataPackage:
            if 'mapDimensions' in node:
                # Sets the max dimensions of the map, only shows up once
                self.simMapDimensionX = node['mapDimensions']['Xdim'] - 1
                self.simMapDimensionY = node['mapDimensions']['Ydim'] - 1
                logging.debug(f"New simulation mapGraph dimensions: X={self.simMapDimensionX}, Y={self.simMapDimensionY}")
                continue

            # Create the node's name from its position data
            nodeName = f"({str(node['nodePosition']['X'])}, {str(node['nodePosition']['Y'])})"
            # Extract the other data
            nodePosition = node['nodePosition']
            nodeType = node['nodeType']
            nodeEdges = node['nodeEdges']
            logging.debug(f"Adding node '{nodeName}':{node}")

            # Add the node to the graph, with its name
            self.simMapGraph.add_node(nodeName, pos=nodePosition, type=nodeType, edgeDirs=nodeEdges)
        logging.info("New simulation mapData nodes successfully loaded to mapGraph.")

        # Add edges based on the node data
        logging.debug("Loading edges to nodes in mapGraph . . .")
        for node in self.simMapGraph.nodes.data():
            # Generate candidate connected nodes
            logging.debug(f"Checking for nodes connected to node: {node}")
            nodeData = node[1]

            # Take the base position
            nodePosition = (nodeData['pos']['X'], nodeData['pos']['Y'])

            logging.debug("Connected to:")
            if nodeData['edgeDirs']['N'] == 1:
                candidateN = str((nodePosition[0], nodePosition[1]-1))
                # Check if the candidate node exists
                if candidateN in self.simMapGraph.nodes:
                    # Check if the candidate node has an edge in this direction
                    if self.simMapGraph.nodes.data()[candidateN]['edgeDirs']['S'] == 1:
                        # print("exists:" + str(candidateN) + "->" + str(node[0]))
                        self.simMapGraph.add_edge(node[0], candidateN)
                        logging.debug(f". . . . .  N: {candidateN}, edge connection added.")

            if nodeData['edgeDirs']['W'] == 1:
                candidateW = str((nodePosition[0]-1, nodePosition[1]))
                # Check if the candidate node exists
                if candidateW in self.simMapGraph.nodes:
                    # Check if the candidate node has an edge in this direction
                    if self.simMapGraph.nodes.data()[candidateW]['edgeDirs']['E'] == 1:
                        # print("exists:" + str(candidateW) + "->" + str(node[0]))
                        self.simMapGraph.add_edge(node[0], candidateW)
                        logging.debug(f". . . . .  W: {candidateW}, edge connection added.")

            if nodeData['edgeDirs']['S'] == 1:
                candidateS = str((nodePosition[0], nodePosition[1]+1))
                # Check if the candidate node exists
                if candidateS in self.simMapGraph.nodes:
                    # Check if the candidate node has an edge in this direction
                    if self.simMapGraph.nodes.data()[candidateS]['edgeDirs']['N'] == 1:
                        # print("exists:" + str(candidateS) + "->" + str(node[0]))
                        self.simMapGraph.add_edge(node[0], candidateS)
                        logging.debug(f". . . . .  S: {candidateS}, edge connection added.")

            if nodeData['edgeDirs']['E'] == 1:
                candidateE = str((nodePosition[0]+1, nodePosition[1]))
                # Check if the candidate node exists
                if candidateE in self.simMapGraph.nodes:
                    # Check if the candidate node has an edge in this direction
                    if self.simMapGraph.nodes.data()[candidateE]['edgeDirs']['W'] == 1:
                        # print("exists:" + str(candidateE) + "->" + str(node[0]))
                        self.simMapGraph.add_edge(node[0], candidateE)
                        logging.debug(f". . . . .  E: {candidateE}, edge connection added.")
        logging.info("New simulation mapData edges loaded.")

        # Update simulation mainView canvas size
        canvasWidth = (self.simMapDimensionX+1)
        canvasHeight = (self.simMapDimensionY+1)
        self.simMapCanvas.setCanvasDimensions(canvasWidth, canvasHeight)
        logging.info("All new simulation mapData finished loading.")

    def updateAgentLocations(self, agentList):
        logging.debug("Updating agent locations in the simulation mapGraph . . .")

        # Remove all agents from the graph
        for node in self.simMapGraph.nodes(data=True):
            if 'agent' in self.simMapGraph.nodes.data()[node[0]]:
                logging.debug(f"Remove agent '{self.simMapGraph.nodes.data()[node[0]]['agent'].ID}:{self.simMapGraph.nodes.data()[node[0]]['agent'].numID}' from simulation node '{node[0]}'.")
                del self.simMapGraph.nodes.data()[node[0]]['agent']
            else:
                pass

        # Insert agents from the agent list back into the graph
        for agent in agentList:
            agentPosition = agentList[agent].position
            targetNode = f"({agentPosition[0]}, {agentPosition[1]})"
            self.simMapGraph.nodes[targetNode]['agent'] = agentList[agent]
            logging.debug(f"Inserted agent '{agentList[agent].ID}:{agent}' into simulation mapGraph node '{targetNode}'.")

        logging.info("Agent data in simulation mapGraph updated.")