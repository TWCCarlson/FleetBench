import tkinter as tk
from tkinter import font as tkFont
import logging
from PIL import Image, ImageTk
import pprint
pp = pprint.PrettyPrinter(indent=4)
from functools import partial
import math

class mainCanvas(tk.Canvas):
    def __init__(self, parent, appearanceValues, ID, gridLoc=None, **kwargs):
        super().__init__(parent)
        self.ID = ID # ID for logging
        self.parent = parent
        self.appearanceValues = appearanceValues
        self.gridLoc = gridLoc  # Grid render location

        # Expose control variables for other objects to trace and act on
        self.currentClickedAgent = tk.StringVar()
        self.hoverText = tk.StringVar()
        self.danglingEdgeVisibility = tk.BooleanVar()
        self.edgeVisibility = tk.BooleanVar()
        self.nodeVisibility = tk.BooleanVar()
        self.agentVisibility = tk.BooleanVar()
        self.agentOrientationVisibility = tk.BooleanVar()

        self.fetchStyleData()

        # Graph should always be rendered into its frame
        self.renderCanvas()

    """
        DATA INITIALIZATION
    """

    def fetchStyleData(self):
        # Pulled from stored values in the class, applied to the tk.Canvas framework
        # self.configure(bg="#313338")
        self["bg"] = self.appearanceValues.simCanvasBackgroundColor
        self["width"] = self.appearanceValues.simCanvasDefaultWidth
        self["height"] = self.appearanceValues.simCanvasDefaultHeight
        self["scrollregion"] = (0, 0, self["width"], self["height"])
        self.canvasTileSize = self.appearanceValues.canvasTileSize
        logging.debug(f"Canvas '{self.ID}' style set.")

    def setCanvasDimensions(self, tileWidth, tileHeight):
        # Canvas width/height are pixel args, but supplied args are in "tiles"
        canvasWidth = tileWidth * self.appearanceValues.simCanvasTileSize
        canvasHeight = tileHeight * self.appearanceValues.simCanvasTileSize
        self.configure(height=canvasHeight, width=canvasWidth, scrollregion=self.bbox("all"))
        self.drawGridlines()
        logging.debug(f"Canvas '{self.ID}' dimensions updated: canvasWidth={tileWidth}, canvasHeight={tileHeight}")

    def renderCanvas(self):
        # If the gridLoc is not supplied, pack the canvas into the frame
        if self.gridLoc == None:
            self.pack()
            logging.info(f"Rendered Canvas '{self.ID}' using pack.")
        elif type(self.gridLoc) == tuple and len(self.gridLoc) == 2:
            # The gridloc is a 2-tuple of (row, column)
            # Needs priority in the frame
            self.parent.columnconfigure(0, weight=1)
            self.parent.rowconfigure(0, weight=1)
            self.grid(row=self.gridLoc[0], column=self.gridLoc[1], sticky="news")
            logging.info(f"Rendered Canvas '{self.ID}' in simulation window using grid.")
        else:
            logging.error(f"Canvas '{self.ID}' location malformed. Did not render.")

    def drawGridlines(self):
        # Mark out the 'tiles' on the canvas, using the tilesize in appearanceValues
        # Horizontal lines
        for i in range(math.floor(int(self["height"])/self.canvasTileSize)+1):
            coords = [0, i*self.canvasTileSize, self["width"], i*self.canvasTileSize]
            self.create_line(*coords, fill=self.appearanceValues.simCanvasGridlineColor)
        # Vertical lines
        for i in range(math.floor(int(self["width"])/self.canvasTileSize)+1):
            coords = [i*self.canvasTileSize, 0, i*self.canvasTileSize, self["height"]]
            self.create_line(*coords ,fill=self.appearanceValues.simCanvasGridlineColor)
        logging.debug(f"Canvas '{self.ID}' rendered grid lines.")

    def ingestGraphData(self, graphRef):
        self.graphRef = graphRef

    def ingestAgentData(self, agentManagerRef):
        self.agentManager = agentManagerRef

    """
        RENDER STATE
    """

    def renderGraphState(self):
        # Run once, on start
        self.renderNodes()
        self.renderEdges()
        self.renderDanglingEdges()
        self.renderAgents()
        self.buildHighlightManager()
        self.generateInfoTiles()
        self.sortCanvasLayers()
        self.setAllLayersVisible()
        self.traceLayerVisibility()
        nodeID = "(2, 2)"
        self.renderTileText(nodeID, "100", tk.NE, "pathfind")
        
    """
        HELPER FUNCTIONS
    """

    def graphCoordToCanvasCoord(self, nodePos):
        # Returns the pixel coordinate at the center of the tile
        return nodePos * self.canvasTileSize + 0.5 * self.canvasTileSize
    
    def canvasCoordToGraphCoord(self, canvasPos):
        return math.floor(canvasPos/self.canvasTileSize)
    
    def convertColorToRGBA(self, color, alpha=1):
        # Pillow interprets alpha as an RGBA value
        if isinstance(color, str) and not color[0] == "#":
            # Named tkinter color
            R, G, B = self.winfo_rgb(color) # these values are 0-65535, Image expects 0-255 integer values
            color = (int(R / 256), int(G / 256), int(B / 256), int(alpha * 255))
        elif isinstance(color, str) and color[0] == "#":
            # Image.new accepts hex colors by default
            pass
        elif isinstance(color, tuple) and len(color) == 3:
            # RGB tuple
            R, G, B = color
            color = (R, G, B, int(alpha * 255))
        return color
    
    """
        OBJECT RENDERS
    """

    def renderNodes(self):
        # Iterate through nodes in the networkX graph
        for node in self.graphRef.nodes.data():
            logging.debug(f"Canvas '{self.ID}' drawing node: {node}")

            # Extract data from the strcuture
            nodeName = node[0]
            nodeData = node[1]
            nodePosX, nodePosY = eval(nodeName)
            nodeType = nodeData["type"]

            # Calculate canvas positions from tile positions
            nodeGraphPosX = self.graphCoordToCanvasCoord(nodePosX)
            nodeGraphPosY = self.graphCoordToCanvasCoord(nodePosY)
            
            # Build the style option arguments for the node
            if nodeType == "edge":
                fillColor = self.appearanceValues.openNodeColor
                nodeSizeRatio = self.appearanceValues.openNodeSizeRatio
                tags = ["node", "openNode"]
            elif nodeType == "charge":
                fillColor = self.appearanceValues.chargeNodeColor
                nodeSizeRatio = self.appearanceValues.chargeNodeSizeRatio
                tags = ["node", "chargeNode"]
            elif nodeType == "deposit":
                fillColor = self.appearanceValues.depositNodeColor
                nodeSizeRatio = self.appearanceValues.depositNodeSizeRatio
                tags = ["node", "depositNode"]
            elif nodeType == "pickup":
                fillColor = self.appearanceValues.pickupNodeColor
                nodeSizeRatio = self.appearanceValues.pickupNodeSizeRatio
                tags = ["node", "pickupNode"]
            elif nodeType == "rest":
                fillColor = self.appearanceValues.restNodeColor
                nodeSizeRatio = self.appearanceValues.restNodeSizeRatio
                tags = ["node", "restNode"]
            elif nodeType == "void":
                # Do nothing, this is empty space
                continue
            logging.debug(f"Node of type {nodeType} is assigned tags: {tags}")

            # Draw the node onto the simulation canvas
            self.create_oval(
                nodeGraphPosX - nodeSizeRatio * self.canvasTileSize,
                nodeGraphPosY - nodeSizeRatio * self.canvasTileSize,
                nodeGraphPosX + nodeSizeRatio * self.canvasTileSize,
                nodeGraphPosY + nodeSizeRatio * self.canvasTileSize,
                fill= fillColor,
                tags=tags
            )
            logging.debug("Canvas node drawn successfully.")
        logging.info(f"Successfully rendered all nodes to Canvas '{self.ID}'.")

    def renderEdges(self):
        # Display connected edges
        for edge in self.graphRef.edges():
            logging.debug(f"Canvas '{self.ID}' attempting to draw edge: {edge}")

            # Edge data is supplied as a tuple of two nodes
            firstNode = edge[0]
            secondNode = edge[1]

            # Break thes tring into a tuple and extract coordinates
            firstPosX, firstPosY = eval(firstNode)
            secondPosX, secondPosY = eval(secondNode)

            # Find the center of the canas tiles
            firstGraphPosX = self.graphCoordToCanvasCoord(firstPosX)
            firstGraphPosY = self.graphCoordToCanvasCoord(firstPosY)
            secondGraphPosX = self.graphCoordToCanvasCoord(secondPosX)
            secondGraphPosY = self.graphCoordToCanvasCoord(secondPosY)

            # Get edge style
            fill = self.appearanceValues.edgeColor
            width = self.appearanceValues.edgeWidth
            tags=["edge"]

            # Draw the edge
            self.create_line(
                firstGraphPosX,
                firstGraphPosY,
                secondGraphPosX,
                secondGraphPosY,
                fill= fill,
                width= width,
                tags= tags,
            )
            logging.debug("Edge drawn successfully.")
        logging.info(f"Rendered all connected graphData edges to Canvas '{self.ID}'.")

    def renderDanglingEdges(self):
        # Edges that exit one node but do not enter another
        # These are not really in the graph, and are only inferred
        for node in self.graphRef.nodes.data():
            # Break out the data
            nodeName = node[0]
            nodeData = node[1]
            nodePosX, nodePosY = eval(nodeName)
            nodeEdges = nodeData["edgeDirs"]

            # Convert tile coordinates to canvas coordinates
            nodeGraphPosX = self.graphCoordToCanvasCoord(nodePosX)
            nodeGraphPosY = self.graphCoordToCanvasCoord(nodePosY)

            # Get styling information
            fill = self.appearanceValues.danglingEdgeColor
            width = self.appearanceValues.danglingEdgeWidth
            tags = ["danglingEdge"]

            # Map the direction of an edge to the resulting translation in the canvas
            edgeDirectionMap = {
                "N": (0, -1),
                "E": (1, 0),
                "W": (-1, 0),
                "S": (0, 1)
            }

            # For potential edge directions in the node data
            for edgeDir, exists in nodeEdges.items():
                if exists:
                    # If there is an edge, calculate its intended target
                    targetNodeX = nodePosX+edgeDirectionMap[edgeDir][0]
                    targetNodeY = nodePosY+edgeDirectionMap[edgeDir][1]
                    targetNodeID = str((targetNodeX, targetNodeY))
                    if targetNodeID not in self.graphRef.neighbors(nodeName):
                        # If it isn't a connected edge, then draw it
                        targetGraphPosX = nodeGraphPosX + 0.5*self.canvasTileSize*edgeDirectionMap[edgeDir][0]
                        targetGraphPosY = nodeGraphPosY + 0.5*self.canvasTileSize*edgeDirectionMap[edgeDir][1]
                        self.create_line(
                            nodeGraphPosX,
                            nodeGraphPosY,
                            targetGraphPosX,
                            targetGraphPosY,
                            fill=fill,
                            width=width,
                            tags=tags
                        )
        logging.info(f"Rendered all unconnected graphData edges on Canvas '{self.ID}'")

    def renderAgents(self):
        # Renders all agents stored as data points in the map graph
        # Should only be used after the canvas is cleared, which we want to avoid doing
        # Otherwise, use the shifting operations 
        for agentID, agent in self.agentManager.agentList.items():
            # Extract agent data
            nodePosX, nodePosY = agent.position
            nodeGraphPosX = self.graphCoordToCanvasCoord(nodePosX)
            nodeGraphPosY = self.graphCoordToCanvasCoord(nodePosY)
            agentOrientation = agent.orientation
            agentID = agent.numID

            # Get styling information
            outline = self.appearanceValues.agentBorderColor
            width = self.appearanceValues.agentBorderWidth
            fill = self.appearanceValues.agentFillColor
            tags = ["agent" + str(agentID), "agent"]
            agentSizeRatio = self.appearanceValues.agentSizeRatio

            # Point transform dict
            pointList = [
                nodeGraphPosX, nodeGraphPosY - agentSizeRatio * self.canvasTileSize,
                nodeGraphPosX - agentSizeRatio * self.canvasTileSize, nodeGraphPosY,
                nodeGraphPosX, nodeGraphPosY + agentSizeRatio * self.canvasTileSize,
                nodeGraphPosX + agentSizeRatio * self.canvasTileSize, nodeGraphPosY
            ]

            # Create agent polygon
            self.create_polygon(
                *pointList,
                outline= outline,
                width= width,
                fill= fill,
                tags= tags
            )

            # Denote agent orientation - this should maybe be broken out to a separate function
            directionMap = {
                "N": (0, -1),
                "E": (1, 0),
                "W": (-1, 0),
                "S": (0, 1)
            }
            indicatorAdjustment = directionMap[agentOrientation]
            
            # Draw the indicator
            width = self.appearanceValues.agentPointerWidth
            tags.append("agentOrientation")
            self.create_line(
                nodeGraphPosX,
                nodeGraphPosY,
                nodeGraphPosX + indicatorAdjustment[0] * self.canvasTileSize * agentSizeRatio,
                nodeGraphPosY + indicatorAdjustment[1] * self.canvasTileSize * agentSizeRatio,
                fill=outline,
                width=width,
                tags=tags
            )

            # To keep the underlying tile visible, reproduce it
            # Get styling information
            width = self.appearanceValues.agentWindowWidth
            tags = ["agent" + str(agentID), "agent", "agentTileWindow"]
            agentWindowSizeRatio = self.appearanceValues.agentWindowRatio
            nodeTypeColorMap = {
                "edge": self.appearanceValues.openNodeColor,
                "charge": self.appearanceValues.chargeNodeColor,
                "deposit": self.appearanceValues.depositNodeColor,
                "pickup": self.appearanceValues.pickupNodeColor,
                "rest": self.appearanceValues.restNodeColor
            }
            # Get the agent's node type->color
            fill = nodeTypeColorMap[self.graphRef.nodes[str(agent.position)]["type"]]

            # Create the "window" circle
            self.create_oval(
                nodeGraphPosX - agentWindowSizeRatio * self.canvasTileSize,
                nodeGraphPosY - agentWindowSizeRatio * self.canvasTileSize,
                nodeGraphPosX + agentWindowSizeRatio * self.canvasTileSize,
                nodeGraphPosY + agentWindowSizeRatio * self.canvasTileSize,
                fill=fill,
                width=width,
                tags=tags
            )
        logging.info(f"Rendered all agents onto Canvas '{self.ID}'")

    """
        INFORMATION HOVER TILES
    """

    def generateInfoTiles(self):
        # This function is called by the infobox to trigger generation of tiles
        self.infoTiles = {}
        # This invisible tile tracks mouseover events to indicate to the user what is in the tile beneath it
        for node in self.graphRef.nodes.data():
            # Extract node data
            nodeID = node[0]
            nodeType = node[1]["type"]
            nodePosX, nodePosY = eval(nodeID)
            nodeGraphPosX = self.graphCoordToCanvasCoord(nodePosX)
            nodeGraphPosY = self.graphCoordToCanvasCoord(nodePosY)
            tags = ["infoTile"]

            # Extract the data
            tileRef, tileID = self.createHighlight(nodeGraphPosX, nodeGraphPosY, alpha=0, fill=(0, 0, 0), tags=tags)
            self.infoTiles[nodeID] = [tileRef, tileID]
        logging.info(f"Generated infoTiles for Canvas '{self.ID}'")

        # Attach mouseover events to the tiles
        self.generateInfoTileEvents()

    def generateInfoTileEvents(self):
        # For each tile, attach mouse interaction events reflecting 
        for tileNode, (tileRef, tileID)  in self.infoTiles.items():
            self.tag_bind(tileID, "<Leave>", self.hoverText.set(". . ."))
            self.tag_bind(tileID, "<Enter>", partial(self.setInfoTileHoverText, tileNode))
            if "agent" in self.graphRef.nodes[tileNode]:
                nodeData = self.graphRef.nodes[tileNode]
                nodeAgentName = nodeData["agent"].ID
                nodeAgentID = nodeData["agent"].numID
                self.tag_bind(tileID, "<Button-1>", partial(self.agentClickHandler, tileNode, nodeAgentName, nodeAgentID))

    def setInfoTileHoverText(self, tileNode, event):
        nodeData = self.graphRef.nodes[tileNode]
        hoverString = f"{str(tileNode)}: {nodeData['type'].capitalize()}"
        if "agent" in nodeData:
            hoverString = hoverString + f", Agent Name: {nodeData['agent'].ID}"
        self.hoverText.set(hoverString)

    def agentClickHandler(self, tileNode, agentName, agentID, event):
        self.requestHighlight(tileNode, "agentHighlight", multi=False)
        self.sortCanvasLayers(targetLayer="agentHighlight", layerMotion="lower")
        self.currentClickedAgent.set(agentName)

    def buildHighlightManager(self):
        # Establishes the format of the highlight manager
        # Holds references to the highlight images to prevent tk garbage collection if multiple highlights are needed
        self.highlightManager = {
            "agentHighlight": [],
            "depositHighlight": [],
            "pickupHighlight": [],
            "pathfindHighlight": []
        }
        logging.info(f"Canvas '{self.ID}' built highlightManager")

    def requestHighlight(self, nodeID, highlightType, multi, color=None, alpha=None):
        # If the requested highlight isn't a multiple highlight, remove highlights of same type
        if highlightType not in self.highlightManager:
            # Restrict highlights to the dict key types
            return
        if not multi:
            # Highlight manager will be a dict where key is string "Type" and values are lists of highlights
            # Clear the highlight object list
            self.highlightManager[highlightType] = []

        # Parse args
        nodePosX, nodePosY = eval(nodeID)
        nodeGraphPosX = self.graphCoordToCanvasCoord(nodePosX)
        nodeGraphPosY = self.graphCoordToCanvasCoord(nodePosY)

        # Fetch style
        if alpha is None:
            # Use default opacity value
            alpha = self.appearanceValues.highlightAlpha

        if color is None:
            # Use default color scheme
            highlightColorDict = {
                "agentHighlight": self.appearanceValues.agentHighlightColor,
                "depositHighlight": self.appearanceValues.depositHighlightColor,
                "pickupHighlight": self.appearanceValues.pickupHighlightColor,
                "pathfindHighlight": self.appearanceValues.pathfindHighlightColor
            }
            fill = highlightColorDict[highlightType]
        else:
            fill = self.convertColorToRGBA(color, alpha)
        tags = ["highlight", highlightType]

        # Create the highlight
        highlightRef, highlightID = self.createHighlight(nodeGraphPosX, nodeGraphPosY, alpha, fill, tags)
        self.highlightManager[highlightType].append(highlightRef) # prevent garbage collection
        self.tag_lower(highlightType)
        logging.info(f"Handled highlight request for node '{nodeID}' of type '{highlightType}'_multi:{multi} on Canvas '{self.ID}'")

    def createHighlight(self, graphPosX, graphPosY, alpha, fill, tags):
        # Highlight the tile
        # This is a fixed-size operation, based on the center of the tile
        # https://stackoverflow.com/questions/54637795/how-to-make-a-tkinter-canvas-rectangle-transparent
        fill = self.convertColorToRGBA(fill, alpha)
        # Create the highlight image, sized to one tile
        image = Image.new('RGBA', (self.canvasTileSize, self.canvasTileSize), fill)
        tkImage = ImageTk.PhotoImage(image) # If this is not saved by reference in memory, it gets garbage collected
        tileImageID = self.create_image(graphPosX, graphPosY, image=tkImage, tags=tags)
        return tkImage, tileImageID
    
    def clearHightlight(self, highlightType=None):
        # Garbage collection will remove all highlights if the references are deleted
        if highlightType is not None:
            self.highlightManager[highlightType] = []
            logging.debug(f"Removed all highlights of type '{highlightType}' from Canvas '{self.ID}'")
        else:
            # Remove all highlights
            for highlightType in self.highlightManager.keys():
                self.highlightManager[highlightType] = []
            logging.debug(f"Removed all highlights from Canvas '{self.ID}'")

    """
        LAYER CONTROLS
    """

    def sortCanvasLayers(self, targetLayer=None, layerMotion=None):
        # Moves layers on the canvas to a default order
        defaultLayerOrder = [
            "highlight",
            "edge",
            "node",
            "agent",
            "infoTile"
        ]
        if targetLayer is None:
            # Sort all layers
            for layer in defaultLayerOrder:
                self.tag_raise(layer)
        else:
            if layerMotion == "raise":
                self.tag_raise(targetLayer)
            elif layerMotion == "lower":
                self.tag_lower(targetLayer)
        logging.debug(f"Layers were re-sorted in Canvas '{self.ID}'")

    def traceLayerVisibility(self):
        layerStates = {
            "danglingEdge": self.danglingEdgeVisibility,
            "edge": self.edgeVisibility,
            "node": self.nodeVisibility,
            "agent": self.agentVisibility,
            "agentOrientation": self.agentOrientationVisibility
        }
        for layerName, layerBool in layerStates.items():
            layerBool.trace_add("write", lambda *args, layerName=layerName, layerBool=layerBool: 
                self.setLayerVisibility(layerName, layerBool.get()))

    def setAllLayersVisible(self):
        self.danglingEdgeVisibility.set(True)
        self.edgeVisibility.set(True)
        self.nodeVisibility.set(True)
        self.agentVisibility.set(True)
        self.agentOrientationVisibility.set(True)

    def checkLayerVisibility(self):
        # Check desired state values
        # Check all desired state values
        layerStates = {
            "danglingEdge": self.danglingEdgeVisibility,
            "edge": self.edgeVisibility,
            "node": self.nodeVisibility,
            "agent": self.agentVisibility,
            "agentOrientation": self.agentOrientationVisibility
        }
        # Iterate, setting the state to match the desired value
        for layer in layerStates:
            self.setLayerVisibility(layer, layerStates[layer])
        logging.info("Updated layer visibilities to match user settings.")

    def setLayerVisibility(self, layerTag, desiredState):
        # Unify the visibility state of all objects with layerTag to match desiredState
        objs = self.find_withtag(layerTag)
        if desiredState == True:
            for obj in objs:
                self.itemconfigure(obj, state='normal')
        elif desiredState == False:
            for obj in objs:
                self.itemconfigure(obj, state='hidden')
        logging.debug(f"Layer '{layerTag}' set to '{desiredState}'")

    """
        ABRITRARY RENDER CALLS
            Methods which render something not related to the data found in the graph
            Pathfinding renders, etc.
    """

    def renderTileText(self, nodeID, text, anchor, type, textColor=None, textFont=None, highlightColor=None, highlightAlpha=None):
        # Process highlight color
        # if highlightAlpha is None:
        #     highlightAlpha = self.appearanceValues.defaultHighlightAlpha
        # if highlightColor is None:
        #     highlightColor=self.appearanceValues.defaultHighlightColor
        
        # Generate highlight tags
        highlightType = type + "Highlight"

        # Highlight the tile
        self.requestHighlight(nodeID, highlightType=highlightType, multi=True, color=highlightColor, alpha=highlightAlpha)

        # Text placement
        nodePosX, nodePosY = eval(nodeID)
        nodeCanvasPosX = self.graphCoordToCanvasCoord(nodePosX)
        nodeCanvasPosY = self.graphCoordToCanvasCoord(nodePosY)
        anchorTextShiftMap = {
            tk.N: (0,-1),
            tk.E: (1, 0),
            tk.W: (-1,0),
            tk.S: (0, 1),
            tk.CENTER: (0, 0),
            tk.NW: (-1, -1),
            tk.NE: (1, -1),
            tk.SW: (-1, 1),
            tk.SE: (1, 1),
        }

        if anchor not in anchorTextShiftMap.keys():
            logging.error(f"Supplied anchor is invalid: {anchor}")
            raise ValueError(f"Anchor invalid: {anchor}")
        
        # Color
        if textColor is None:
            textColor = "black"
        else:
            textColor = self.convertColorToRGBA(textColor, alpha=1)
        # Fontspec
        if textFont is None:
            textFont = tkFont.Font(weight="bold", size=self.appearanceValues.highlightTextSize)
        # Tags
        tags = ["text", type + "Text"]

        nodeTextPosX = nodeCanvasPosX + anchorTextShiftMap[anchor][0] * 0.5 * self.canvasTileSize
        nodeTextPosY = nodeCanvasPosY + anchorTextShiftMap[anchor][1] * 0.5 * self.canvasTileSize
        self.create_text(nodeTextPosX, nodeTextPosY, text=text, anchor=anchor, fill=textColor, font=textFont, tags=tags)