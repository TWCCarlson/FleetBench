import tkinter as tk
from tkinter import font as tkFont
import logging
from PIL import Image, ImageTk
import pprint
pp = pprint.PrettyPrinter(indent=4)
from functools import partial
import math

class mainCanvas(tk.Canvas):
    def __init__(self, parent, appearanceValues, ID, gridLoc=None, bg=None, width=None, height=None, tileSize=None, gridlineColor=None, **kwargs):
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

        # Style settings
        if bg is None:
            bg = self.appearanceValues.canvasBackgroundColor
        if width is None:
            width = self.appearanceValues.canvasDefaultWidth
        if height is None:
            height = self.appearanceValues.canvasDefaultHeight
        if tileSize is None:
            tileSize = self.appearanceValues.canvasTileSize
        if gridlineColor is None:
            gridlineColor = self.appearanceValues.canvasGridlineColor
        self.setCanvasStyle(bg, width, height, tileSize, gridlineColor)

        # Build render queue storage
        self.renderQueue = []

        # Graph should always be rendered into its frame
        self.renderCanvas()

    """
        DATA INITIALIZATION
    """

    def setCanvasStyle(self, bg, width, height, tileSize, gridlineColor):
        # Pulled from stored values in the class, applied to the tk.Canvas framework
        # self.configure(bg="#313338")
        self["bg"] = bg
        self["width"] = width
        self["height"] = height
        self["scrollregion"] = (0, 0, self["width"], self["height"])
        self.canvasTileSize = tileSize
        self.gridlineColor = gridlineColor
        logging.debug(f"Canvas '{self.ID}' style set.")

    def setCanvasDimensions(self, tileWidth, tileHeight):
        # Canvas width/height are pixel args, but supplied args are in "tiles"
        canvasWidth = tileWidth * self.canvasTileSize
        canvasHeight = tileHeight * self.canvasTileSize
        self.configure(height=canvasHeight, width=canvasWidth, scrollregion=self.bbox("all"))
        logging.debug(f"Canvas '{self.ID}' dimensions updated: canvasWidth={tileWidth}, canvasHeight={tileHeight}")

    def renderCanvas(self, *args):
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
            self.create_line(*coords, fill=self.gridlineColor)
        # Vertical lines
        for i in range(math.floor(int(self["width"])/self.canvasTileSize)+1):
            coords = [i*self.canvasTileSize, 0, i*self.canvasTileSize, self["height"]]
            self.create_line(*coords ,fill=self.gridlineColor)
        logging.debug(f"Canvas '{self.ID}' rendered grid lines.")

    def ingestGraphData(self, graphRef):
        self.graphRef = graphRef

    def ingestAgentData(self, agentManagerRef):
        self.agentManager = agentManagerRef

    """
        RENDER STATE
    """

    def initialRender(self):
        self.drawGridlines()

    def renderGraphState(self):
        # Run once, on start
        self.drawGridlines()
        self.renderNodes()
        self.renderEdges()
        self.renderDanglingEdges()
        self.renderAgents()
        self.buildHighlightManager()
        self.generateInfoTiles()
        self.sortCanvasLayers()
        self.setAllLayersVisible()
        self.traceLayerVisibility()

    def requestRender(self, renderType, renderAction, renderData):
        # Maintains a list of things to do on the next render step
        acceptedRenderTypes = {
            "agent": {
                "move": self.moveAgentObject,
                "rotate": self.rotateAgentObject,
                "delete": self.deleteAgentObject,
                "new": self.newAgentObject,
                "clear": self.clearAgentObjects
            },
            "highlight": {
                "move": self.moveHighlightObject,
                "delete": self.deleteHighlightObject,
                "new": self.newHighlightObject,
                "clear": self.clearHighlightObjects
            },
            "canvasLine": {
                "new": self.newCanvasLineObject,
                "delete": self.deleteCanvasLineObject,
                "extend": self.extendCanvasLineObject,
                "clear": self.clearCanvasLineObjects
            },
            "text": {
                "new": self.newTextObject,
                "delete": self.deleteTextObject,
                "clear": self.clearTextObjects,
                # "edit": print("editText")
            },
            "canvas": {
                "clear": self.clearCanvasObjects,
                "render": self.renderCanvasObjects
            }
        }
        if renderType in acceptedRenderTypes:
            actionFunction = acceptedRenderTypes[renderType][renderAction]
        self.renderQueue.append((actionFunction, renderData))

    def handleRenderQueue(self):
        while len(self.renderQueue) != 0:
            (action, data) = self.renderQueue.pop(0)
            action(data)
        self.sortCanvasLayers()

    def moveAgentObject(self, renderData):
        # Get tag, source, target nodes
        agentNumID = renderData["agentNumID"]
        sourceNodeID = renderData["sourceNodeID"]
        targetNodeID = renderData["targetNodeID"]
        # Convert to canvas coordinates
        sourceNodeCanvasPosX, sourceNodeCanvasPosY = self.nodeToCanvasTile(sourceNodeID)
        targetNodeCanvasPosX, targetNodeCanvasPosY = self.nodeToCanvasTile(targetNodeID)
        # Get and shift all tagged objects
        objs = self.find_withtag("agent" + str(agentNumID))
        for obj in objs:
            self.move(obj, targetNodeCanvasPosX-sourceNodeCanvasPosX, targetNodeCanvasPosY-sourceNodeCanvasPosY)

    def rotateAgentObject(self, renderData):
        agentNumID = renderData["agentNumID"]
        newOrientation = renderData["orientation"]
        agentPosition = renderData["position"]
        # Remove the current orientation mark
        objs = self.find_withtag("agent" + str(agentNumID))
        for obj in objs:
            tags = self.gettags(obj)
            if "agentOrientation" in tags:
                self.delete(obj)
        # Create the new orientation mark
        nodeGraphPosX, nodeGraphPosY = self.nodeToCanvasTile(agentPosition)
        self.createAgentOrientation(nodeGraphPosX, nodeGraphPosY, newOrientation, agentNumID)

    def deleteAgentObject(self, renderData):
        self.delete("agent" + str(renderData["agentNumID"]))

    def newAgentObject(self, renderData):
        # Create a new agent, exposing style options
        agentPos = renderData["position"] # req'd
        agentNumID = renderData["agentNumID"] # req'd
        agentColor = renderData.get("color", None) #optional
        agentOrientation = renderData.get("orientation", None) #optional
        self.createAgent(agentPos, agentNumID, agentColor=agentColor, agentOrientation=agentOrientation)
    
    def clearAgentObjects(self, renderData):
        self.delete("agent")
        regen = renderData.get("regenerate", False)
        if regen:
            self.renderAgents()

    def moveHighlightObject(self, renderData):
        newPos = renderData["position"]
        highlightTag = renderData["highlightTag"]
        newCanvasPosX, newCanvasPosY = self.nodeToCanvasTile(newPos)
        newCanvasPosX = newCanvasPosX - 0.5 * self.canvasTileSize
        newCanvasPosY = newCanvasPosY - 0.5 * self.canvasTileSize
        # Find a specifically tagged highlight, and shift it to a new position
        obj = self.find_withtag(highlightTag)
        self.moveto(obj, newCanvasPosX, newCanvasPosY)

    def deleteHighlightObject(self, renderData):
        self.delete(renderData["highlightTag"])

    def newHighlightObject(self, renderData):
        nodeID = renderData["targetNodeID"] #req'd
        highlightType = renderData["highlightType"] #req'd
        multi = renderData["multi"] #req'd
        color = renderData.get("color", None) #optional
        alpha = renderData.get("alpha", None) #optional
        highlightTags = renderData.get("highlightTags", None) #optional
        self.requestHighlight(nodeID, highlightType, multi, color=color, alpha=alpha, highlightTags=highlightTags)

    def clearHighlightObjects(self, renderData):
        self.delete("highlight")

    def newCanvasLineObject(self, renderData):
        nodePath = renderData["nodePath"] #req'd
        lineType = renderData["lineType"] #req'd
        color = renderData.get("color", None) #optional
        width = renderData.get("width", None) #optional
        self.renderDirectionArrow(nodePath, lineType, color=color, width=width)

    def deleteCanvasLineObject(self, renderData):
        if isinstance(renderData["oldNodePath"][0], str):
            oldNodePath = tuple(eval(node) for node in renderData["oldNodePath"])
        else:
            oldNodePath = tuple(renderData["oldNodePath"])
        obj = self.find_withtag(oldNodePath)
        self.delete(obj)

    def extendCanvasLineObject(self, renderData):
        # The node path was saved as a tag, so it is searchable
        if isinstance(renderData["oldNodePath"][0], str):
            oldNodePath = tuple(eval(node) for node in renderData["oldNodePath"])
        else:
            oldNodePath = tuple(renderData["oldNodePath"])
        obj = self.find_withtag(oldNodePath)
        tags = list(self.gettags(obj))
        if tags:
            extensionPath = renderData["pathExtension"]
            fill = self.itemcget(obj, "fill")
            width = self.itemcget(obj, "width")
            lineType = tags.pop(1)
            newPath = oldNodePath + tuple(eval(node) for node in extensionPath)
            self.delete(obj)
            self.renderDirectionArrow(newPath, lineType, color=fill, width=width)

    def clearCanvasLineObjects(self, *args):
        # Possible this should be expanded into a general arrows method with variable tag acceptance
        self.delete("canvasLine")

    def newTextObject(self, renderData):
        nodeID = renderData["position"]
        text = renderData["text"]
        textType = renderData["textType"]
        anchor = renderData.get("anchor", None)
        textColor = renderData.get("textColor", None)
        textFont = renderData.get("textFont", None)
        self.renderTileText(nodeID, text, textType, anchor, textColor, textFont)

    def deleteTextObject(self, renderData):
        self.delete(renderData["textType"])

    def clearTextObjects(self, *args):
        # Currently there is nothing unique about each piece of text, so all are cleared
        self.delete("text")

    def clearCanvasObjects(self, *args):
        self.delete("all")

    def renderCanvasObjects(self, *args):
        self.drawGridlines()
        self.renderGraphState()

    def processRenderRequests(self):
        # Iterates through the list of rendering operations
        pass
        
    """
        HELPER FUNCTIONS
    """

    def graphCoordToCanvasCoord(self, nodePos):
        if isinstance(nodePos, str):
            nodePos = eval(nodePos)
        # Returns the pixel coordinate at the center of the tile
        return nodePos * self.canvasTileSize + 0.5 * self.canvasTileSize
    
    def canvasCoordToGraphCoord(self, canvasPos):
        return math.floor(canvasPos/self.canvasTileSize)
    
    def nodeToCanvasTile(self, nodeID):
        if isinstance(nodeID, str):
            nodeX, nodeY = eval(nodeID)
            nodeXPos = self.graphCoordToCanvasCoord(nodeX)
            nodeYPos = self.graphCoordToCanvasCoord(nodeY)
        elif isinstance(nodeID, tuple) and len(nodeID)==2:
            nodeX, nodeY = nodeID
            nodeXPos = self.graphCoordToCanvasCoord(nodeX)
            nodeYPos = self.graphCoordToCanvasCoord(nodeY)
        return (nodeXPos, nodeYPos)
    
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
            nodeGraphPosX, nodeGraphPosY = self.nodeToCanvasTile(agent.position)
            agentOrientation = agent.orientation
            agentID = agent.numID
            # Create the 3 components making up an "agent" in the canvas representation
            self.createAgentBody(nodeGraphPosX, nodeGraphPosY, agentID)
            self.createAgentOrientation(nodeGraphPosX, nodeGraphPosY, agentOrientation, agentID)
            self.createAgentTileWindow(nodeGraphPosX, nodeGraphPosY, agent.position, agentID)
        logging.info(f"Rendered all agents onto Canvas '{self.ID}'")

    def createAgent(self, agentPosition, agentID, agentColor=None, agentOrientation=None):
        # Extract data from the agent
        nodeGraphPosX, nodeGraphPosY = self.nodeToCanvasTile(agentPosition)
        agentOrientation = agentOrientation
        agentID = agentID

        # Create the 3 components making up an "agent" in the canvas representation
        self.createAgentBody(nodeGraphPosX, nodeGraphPosY, agentID, fillColor=agentColor)
        self.createAgentOrientation(nodeGraphPosX, nodeGraphPosY, agentOrientation, agentID)
        self.createAgentTileWindow(nodeGraphPosX, nodeGraphPosY, agentPosition, agentID)

    def createAgentBody(self, nodeGraphPosX, nodeGraphPosY, agentID, fillColor=None):
        # Body is a diamond, accept optional fillColor args
        outline = self.appearanceValues.agentBorderColor
        width = self.appearanceValues.agentBorderWidth
        if fillColor is None:
            fillColor = self.appearanceValues.agentFillColor
        agentSizeRatio = self.appearanceValues.agentSizeRatio
        tags = ["agent" + str(agentID), "agent"]

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
            fill= fillColor,
            tags= tags
        )

    def createAgentOrientation(self, nodeGraphPosX, nodeGraphPosY, agentOrientation, agentID):
        # Orientation is a line extending beyond the window size to the edge of the body
        agentSizeRatio = self.appearanceValues.agentSizeRatio
        width = self.appearanceValues.agentPointerWidth
        tags = ["agent" + str(agentID), "agent", "agentOrientation"]
        outline = self.appearanceValues.agentBorderColor

        # Point transform dict
        directionMap = {
            "N": (0, -1),
            "E": (1, 0),
            "W": (-1, 0),
            "S": (0, 1)
        }
        if agentOrientation is not None:
            indicatorAdjustment = directionMap[agentOrientation]
        else:
            indicatorAdjustment = directionMap["N"]

        # Draw the indicator
        self.create_line(
            nodeGraphPosX,
            nodeGraphPosY,
            nodeGraphPosX + indicatorAdjustment[0] * self.canvasTileSize * agentSizeRatio,
            nodeGraphPosY + indicatorAdjustment[1] * self.canvasTileSize * agentSizeRatio,
            fill=outline,
            width=width,
            tags=tags
        )

    def createAgentTileWindow(self, nodeGraphPosX, nodeGraphPosY, agentPosition, agentID):
        # Window is a circle of same color as the tile beneath
        width = self.appearanceValues.agentWindowWidth
        tags = ["agent" + str(agentID), "agent", "agentTileWindow"]
        agentWindowSizeRatio = self.appearanceValues.agentWindowRatio
        # Reproduce the underlying tile's color
        nodeTypeColorMap = {
            "edge": self.appearanceValues.openNodeColor,
            "charge": self.appearanceValues.chargeNodeColor,
            "deposit": self.appearanceValues.depositNodeColor,
            "pickup": self.appearanceValues.pickupNodeColor,
            "rest": self.appearanceValues.restNodeColor
        }
        # Get the agent's node type->color
        fill = nodeTypeColorMap[self.graphRef.nodes[str(agentPosition)]["type"]]

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
        # For each tile, attach mouse interaction events reflecting contents of the tile
        for tileNode, (tileRef, tileID)  in self.infoTiles.items():
            self.tag_bind(tileID, "<Leave>", self.hoverText.set(". . ."))
            self.tag_bind(tileID, "<Enter>", partial(self.setInfoTileHoverText, tileNode))
            self.tag_bind(tileID, "<Button-1>", partial(self.agentSelectHandler, tileNode))

    def setInfoTileHoverText(self, tileNode, event):
        nodeData = self.graphRef.nodes[tileNode]
        hoverString = f"{str(tileNode)}: {nodeData['type'].capitalize()}"
        if "agent" in nodeData:
            hoverString = hoverString + f", Agent Name: {nodeData['agent'].ID}"
        self.hoverText.set(hoverString)

    def agentSelectHandler(self, tileNode, event=None):
        nodeData = self.graphRef.nodes[tileNode]
        if "agent" in nodeData:
            agentName = nodeData["agent"].ID
            agentNumID = nodeData["agent"].numID
            self.requestHighlight(tileNode, "agentHighlight", multi=False, highlightTags=["agent" + str(agentNumID) + "Highlight"])
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

    def requestHighlight(self, nodeID, highlightType, multi, color=None, alpha=None, highlightTags=None):
        # If the requested highlight isn't a multiple highlight, remove highlights of same type
        if highlightType not in self.highlightManager:
            # Restrict highlights to the dict key types
            return
        if not multi:
            # Highlight manager will be a dict where key is string "Type" and values are lists of highlights
            # Clear the highlight object list
            self.highlightManager[highlightType] = []

        # Parse args
        nodeGraphPosX, nodeGraphPosY = self.nodeToCanvasTile(nodeID)

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
        if highlightTags is not None:
            tags = tags + highlightTags

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
            "danglingEdge",
            "node",
            "agent",
            "canvasLine",
            "infoTile",
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

    def renderTileText(self, nodeID, text, textType, anchor=None, textColor=None, textFont=None):
        # Text placement
        nodeCanvasPosX, nodeCanvasPosY = self.nodeToCanvasTile(nodeID)
        anchorTextShiftMap = {
            tk.N: (0, -1),
            tk.E: (1, 0),
            tk.W: (-1, 0),
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
        if anchor is None:
            anchor = tk.NE
        
        # Color
        if textColor is None:
            textColor = self.appearanceValues.defaultTextColor

        # Fontspec
        if textFont is None:
            textFont = tkFont.Font(weight="bold", size=self.appearanceValues.highlightTextSize)
        # Tags
        tags = ["text", textType + "Text", textType]

        nodeTextPosX = nodeCanvasPosX + anchorTextShiftMap[anchor][0] * 0.5 * self.canvasTileSize
        nodeTextPosY = nodeCanvasPosY + anchorTextShiftMap[anchor][1] * 0.5 * self.canvasTileSize
        self.create_text(nodeTextPosX, nodeTextPosY, text=text, anchor=anchor, fill=textColor, font=textFont, tags=tags)

    def renderDirectionArrow(self, nodePath, lineType, color=None, width=None):
        # NodePath is a list of nodes visited by the arrow, in order of visitation
        if isinstance(nodePath[0], str):
            tagPath = tuple(eval(node) for node in nodePath)
        else:
            tagPath = tuple(nodePath)
        convertedNodePath = []
        for i, node in enumerate(nodePath):
            posCanvasX, posCanvasY = self.nodeToCanvasTile(node)
            convertedNodePath.append((posCanvasX, posCanvasY))

        # Style settings
        if color is None:
            color = self.appearanceValues.canvasArrowDefaultColor
        if width is None:
            width = self.appearanceValues.canvasArrowDefaultWidth

        # Generate tags
        tags = ["canvasLine", lineType, tagPath]


        # Render the line
        self.create_line(convertedNodePath, fill=color, arrow=tk.LAST, width=width, tags=tags)