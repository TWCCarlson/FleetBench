import tkinter as tk
import math
import logging
import pprint
pp = pprint.PrettyPrinter(indent=4)
from functools import partial
from PIL import Image, ImageDraw, ImageTk

from modules.mainCanvas import mainCanvas

class simMainView(tk.Frame):
    """
        The primary viewfield of the warehouse
        Drawn using tk.Canvas to display robot, task, and map information
    """
    def __init__(self, parent):
        logging.debug("Simulation Main View UI Element initializing . . .")
        self.parent = parent

        # Fetch styling configuration
        self.appearanceValues = self.parent.parent.parent.appearance
        frameHeight = self.appearanceValues.simulationMainViewHeight
        frameWidth = self.appearanceValues.simulationMainViewWidth
        frameBorderWidth = self.appearanceValues.frameBorderWidth
        frameRelief = self.appearanceValues.frameRelief
        logging.debug("Style information retrieved.")

        # Declare the mainView frame
        tk.Frame.__init__(self, parent,
            height=frameHeight,
            width=frameWidth,
            borderwidth=frameBorderWidth,
            relief=frameRelief)
        logging.debug("Containing frame settings built.")

        # Render the frame
        self.grid_propagate(False)
        self.grid(row=1, column=0, sticky=tk.N, rowspan=2)
        logging.debug("Containing frame rendered.")

        # Build the mainView canvas
        # mapGraphRef = self.parent.parent.simulationProcess.simGraphData.simMapGraph
        # self.simCanvas = simCanvas(self, self.appearanceValues)
        self.simCanvas = mainCanvas(self, self.appearanceValues, "simCanvas", gridLoc=(0, 0))
        logging.debug("Simulation canvas rendered.")

        # Create scrollbars
        self.initScrolling()
        logging.info("Simulation Main Canvas UI elements finished building.")

    def initScrolling(self):
        # Create scrollbar components
        self.xbar = tk.Scrollbar(self, orient="horizontal")
        self.ybar = tk.Scrollbar(self, orient="vertical")
        logging.debug("Scrollbar component classes built.")

        # Bind scrollbar state to canvas view window state
        self.xbar["command"] = self.simCanvas.xview
        self.ybar["command"] = self.simCanvas.yview
        logging.debug("Bound scrollbars to simulation canvas view window.")

        # Adjust positioning, size relative to grid
        self.xbar.grid(column=0, row=1, sticky="ew")
        self.ybar.grid(column=1, row=0, sticky="ns")
        logging.debug("Rendered canvas scrollbars")

        # Make canvas update scrollbar position to match the view window state
        self.simCanvas["xscrollcommand"] = self.xbar.set
        self.simCanvas["yscrollcommand"] = self.ybar.set
        logging.debug("Mains canvas scroll commands bound to scrollbar states.")

        # Bind mousewheel to interact with the scrollbars
        # Only bound while cursor is inside the frame
        self.bind('<Enter>', self.bindMousewheel)
        self.bind('<Leave>', self.unbindMousewheel)

        # Reset the view
        self.simCanvas.xview_moveto("0.0")
        self.simCanvas.yview_moveto("0.0")
        logging.debug("Simulation scrollbars and canvas default view window set.")

    def bindMousewheel(self, event):
        self.bind_all("<MouseWheel>", self.mousewheelAction)
        self.bind_all("<Shift-MouseWheel>", self.shiftMousewheelAction)
        logging.debug("Bound mousewheel inputs to simulation main canvas scrollbars.")

    def unbindMousewheel(self, event):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Shift-MouseWheel>")
        logging.debug("Released mousewheel inputs to simulation main canvas scrollbars.")

    def mousewheelAction(self, event):
        self.simCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def shiftMousewheelAction(self, event):
        self.simCanvas.xview_scroll(int(-1*(event.delta/120)), "units")

class simCanvas(tk.Canvas):
    """
        The primary view used within the simulation window to view the activity in he warehouse
    """
    def __init__(self, parent, appearanceValues):
        logging.debug("Building the simulation main canvas . . .")

        tk.Canvas.__init__(self, parent)
        self.parent = parent

        # Style
        self.appearanceValues = appearanceValues
        self["bg"] = self.appearanceValues.simCanvasBackgroundColor
        self["width"] = self.appearanceValues.simCanvasDefaultWidth
        self["height"] = self.appearanceValues.simCanvasDefaultHeight
        self["scrollregion"] = (0, 0, self["width"], self["height"])
        self.canvasTileSize = self.appearanceValues.canvasTileSize
        logging.info("Simulation Main Canvas UI element style settings built.")

        # Render canvas
        # Use config to give it size priority over scrollbars
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.grid(column=0, row=0, sticky=tk.N+tk.S+tk.E+tk.W)
        logging.info("Rendered Simulation Main Canvas in simulation window.")

        # Draw gridlines
        self.drawGridlines()

        # Set default layer visibilities
        self.setAllLayersVisible()
        
        # Initialize highlight containers
        self.images = {}

    def drawGridlines(self):
        # Drawn for every linewidth in appearanceValues
        logging.debug("Rendering Simulation Main Canvas gridlines . . .")
        # Horizontal lines
        for i in range(math.floor(int(self["height"])/self.canvasTileSize)+1):
            self.create_line(0, i*self.canvasTileSize, self["width"], i*self.canvasTileSize, fill=self.appearanceValues.simCanvasGridlineColor)
        # Vertical lines
        for i in range(math.floor(int(self["width"])/self.canvasTileSize)+1):
            self.create_line(i*self.canvasTileSize, 0, i*self.canvasTileSize, self["height"], fill=self.appearanceValues.simCanvasGridlineColor)
        
    def setCanvasDimensions(self, tileWidth, tileHeight):
        # Adjusts the canvas to have passed dimensions (in number of tiles)
        canvasWidth = tileWidth * self.appearanceValues.simCanvasTileSize
        canvasHeight = tileHeight * self.appearanceValues.simCanvasTileSize
        self["width"] = canvasWidth
        self["height"] = canvasHeight
        self["scrollregion"] = (0, 0, canvasWidth, canvasHeight)
        logging.debug(f"Main Canvas dimensions updated: canvasWidth={tileWidth}, canvasHeight={tileHeight}")

    def graphCoordToCanvas(self, coord):
        # Converts the tile number to the canvas pixel number
        # In: integer id of a tile
        # Out: central pixel of the corresponding location in the canvas
        tileSize = self.appearanceValues.simCanvasTileSize
        canvasCoord = coord * tileSize + 0.5 * tileSize
        logging.debug(f"Converted tile coordinate '{coord}' to canvas coordinate '{canvasCoord}'")
        return canvasCoord

    def renderGraphState(self):
        # Reset the canvas to being empty before redrawing
        self.clearMainCanvas()
        logging.info("Cleared simulation main canvas for re-rendering.")

        # Retrieve mainView styling information
        tileSize = self.appearanceValues.simCanvasTileSize
        nodeSizeRatio = self.appearanceValues.simCanvasTileCircleRatio
        edgeWidth = self.appearanceValues.simCanvasEdgeWidth
        logging.info("Fetched style reference values.")

        # Retrieve the graph information
        mapGraph = self.parent.parent.parent.simulationProcess.simGraphData.simMapGraph

        # Render grid lines
        logging.info("Attempting to render simulation canvas gridlines . . .")
        self.drawGridlines()

        # Render the mapGraph nodes
        logging.info("Attempting to render simulation map nodes . . .")
        self.renderNodes(mapGraph, tileSize, nodeSizeRatio)

        # Render the mapGraph connected edges
        logging.info("Attempting to render simulation map connected edges . . .")
        self.renderEdges(mapGraph, edgeWidth)

        # Render the mapGraph unconnected edges
        logging.info("Attempting to render simulation map unconnected edges . . .")
        self.renderDanglingEdges(mapGraph, tileSize, edgeWidth)

        # Render the location of all agents
        logging.info("Attempting to render simulation agent positions . . .")
        self.renderAgents(mapGraph, tileSize)

        # Create mouse hover info elements
        logging.info("Attempting to render simulation hover info . . .")
        self.generateHoverInfo(mapGraph, tileSize)

        # Sort canvas objects into the correct layer viewing order
        logging.info("Attempting to sort canvas layers . . .")
        self.sortCanvasLayers()

        # Check whether a layer should be visible
        logging.info("Setting layer visibility on simulation main canvas . . .")
        self.checkLayerVisibility()

        logging.info("Canvas re-render finished.")

    def renderNodes(self, mapGraph, tileSize, nodeSizeRatio):
        # Iterate through the graph and draw nodes onto the simulation main view canvas
        for node in mapGraph.nodes.data():
            logging.debug(f"Simulation attempting to draw node: {node}")

            # Extract data
            nodeData = node[1]
            nodePosX = nodeData["pos"]["X"]
            nodePosY = nodeData["pos"]["Y"]
            nodeType = nodeData["type"]

            # Locate the canvas position of the tile
            nodePosGraphX = self.graphCoordToCanvas(nodePosX)
            nodePosGraphY = self.graphCoordToCanvas(nodePosY)

            # Set the node style
            if nodeType == "edge":
                fillColor = "blue"
                tags = ["node", "openNode"]
            elif nodeType == "charge":
                fillColor = "yellow"
                tags = ["node", "chargeNode"]
            elif nodeType == "deposit":
                fillColor = "light green"
                tags = ["node", "depositNode"]
            elif nodeType == "pickup":
                fillColor = "light blue"
                tags = ["node", "pickupNode"]
            elif nodeType == "rest":
                fillColor = "brown"
                tags = ["node", "restNode"]
            elif nodeType == "void":
                # Do nothing
                logging.debug(f"Simulation node is of type 'void', ignoring . . .")
                continue
            logging.debug(f"Simulation node type '{nodeType}' is assigned tags: {tags}")

            # Draw the node onto the simulation canvas
            self.create_oval(
                nodePosGraphX - nodeSizeRatio * tileSize,
                nodePosGraphY - nodeSizeRatio * tileSize,
                nodePosGraphX + nodeSizeRatio * tileSize,
                nodePosGraphY + nodeSizeRatio * tileSize,
                fill=fillColor,
                tags=tags
            )
            logging.debug("Node drawn on the successfully.")
        logging.info("Rendered all graphData nodes to the simulation canvas.")

    def renderEdges(self, graphData, edgeWidth):
        # Display connected edges
        for edge in graphData.edges():
            logging.debug(f"Attempting to draw edge: {edge}")
            # Break the edge into its 2 nodes
            firstPoint = edge[0]
            secondPoint = edge[1]

            # Break the string into a tuple and pull out the coordinates
            firstPosX = eval(firstPoint)[0]
            firstPosY = eval(firstPoint)[1]
            secondPosX = eval(secondPoint)[0]
            secondPosY = eval(secondPoint)[1]

            # Find the center of the relevant tiles on the canvas
            logging.debug("Identifying canvas coordinates the edge begins at:")
            firstPosGraphX = self.graphCoordToCanvas(firstPosX)
            firstPosGraphY = self.graphCoordToCanvas(firstPosY)
            logging.debug("Identifying canvas coordinates the edge ends at:")
            secondPosGraphX = self.graphCoordToCanvas(secondPosX)
            secondPosGraphY = self.graphCoordToCanvas(secondPosY)

            # Draw the edge
            self.create_line(
                firstPosGraphX,
                firstPosGraphY,
                secondPosGraphX,
                secondPosGraphY,
                fill = "blue",
                width = edgeWidth,
                tags=["edge"]
            )
            logging.debug("Edge drawn successfully.")
        logging.info("Rendered all connected graphData edges.")

    def renderDanglingEdges(self, graphData, tileSize, edgeWidth):
        # Render edges that are in the mapfile but not connected to another node
        for node in graphData.nodes.data():
            # Break out the data
            nodeName = node[0]
            nodeData = node[1]
            nodePosX = nodeData["pos"]["X"]
            nodePosY = nodeData["pos"]["Y"]
            nodeEdges = nodeData["edgeDirs"]
            logging.debug(f"Checking node '{nodeName}' for unconnected edges in the graph.")
            # If the node has an edge in a direction
            if nodeEdges["N"] == 1:
                # Calculate what the node it is trying to connect to should be
                edgeTarget = "(" + str(nodePosX) + ", " + str(nodePosY-1) + ")"
                # Check that node is not connected to target by a real edge
                if graphData.has_edge(nodeName, edgeTarget):
                # if edgeTarget in graphData.neighbors(nodeName):
                    pass
                else:
                    logging.debug(f"'{nodeName}' has an unconnected edge toward '{edgeTarget}'.")
                    # Draw the line if it dangles and tag it appropriately
                    nodePosGraphX = self.graphCoordToCanvas(nodePosX)
                    nodePosGraphY = self.graphCoordToCanvas(nodePosY)
                    self.create_line(
                        nodePosGraphX,
                        nodePosGraphY,
                        nodePosGraphX,
                        nodePosGraphY - 0.5*tileSize,
                        fill="green",
                        width=edgeWidth,
                        tags=["danglingEdge"]
                    )
                    logging.debug("Unconnected edge drawn.")
            if nodeEdges["E"] == 1:
                # Calculate what the node it is trying to connect to should be
                edgeTarget = "(" + str(nodePosX+1) + ", " + str(nodePosY) + ")"
                # Check that node is not connected to target by a real edge
                if graphData.has_edge(nodeName, edgeTarget):
                    pass
                else:
                    logging.debug(f"'{nodeName}' has an unconnected edge toward '{edgeTarget}'.")
                    # Draw the line if it dangles and tag it appropriately
                    nodePosGraphX = self.graphCoordToCanvas(nodePosX)
                    nodePosGraphY = self.graphCoordToCanvas(nodePosY)
                    self.create_line(
                        nodePosGraphX,
                        nodePosGraphY,
                        nodePosGraphX + 0.5*tileSize,
                        nodePosGraphY,
                        fill="green",
                        width=edgeWidth,
                        tags=["danglingEdge"]
                    )
                    logging.debug("Unconnected edge drawn.")
            if nodeEdges["W"] == 1:
                # Calculate what the node it is trying to connect to should be
                edgeTarget = "(" + str(nodePosX-1) + ", " + str(nodePosY) + ")"
                # Check that node is not connected to target by a real edge
                if edgeTarget in graphData.neighbors(nodeName):
                    pass
                else:
                    logging.debug(f"'{nodeName}' has an unconnected edge toward '{edgeTarget}'.")
                    # Draw the line if it dangles and tag it appropriately
                    nodePosGraphX = self.graphCoordToCanvas(nodePosX)
                    nodePosGraphY = self.graphCoordToCanvas(nodePosY)
                    self.create_line(
                        nodePosGraphX,
                        nodePosGraphY,
                        nodePosGraphX - 0.5*tileSize,
                        nodePosGraphY,
                        fill="green",
                        width=edgeWidth,
                        tags=["danglingEdge"]
                    )
                    logging.debug("Unconnected edge drawn.")
            if nodeEdges["S"] == 1:
                # Calculate what the node it is trying to connect to should be
                edgeTarget = "(" + str(nodePosX) + ", " + str(nodePosY+1) + ")"
                # Check that node is not connected to target by a real edge
                if edgeTarget in graphData.neighbors(nodeName):
                    pass
                else:
                    logging.debug(f"'{nodeName}' has an unconnected edge toward '{edgeTarget}'.")
                    # Draw the line if it dangles and tag it appropriately
                    nodePosGraphX = self.graphCoordToCanvas(nodePosX)
                    nodePosGraphY = self.graphCoordToCanvas(nodePosY)
                    self.create_line(
                        nodePosGraphX,
                        nodePosGraphY,
                        nodePosGraphX,
                        nodePosGraphY + 0.5*tileSize,
                        fill="green",
                        width=edgeWidth,
                        tags=["danglingEdge"]
                    )
                    logging.debug("Unconnected edge drawn.")
        logging.info("Rendered all unconnected graphData edges.")

    def agentClickHighlighter(self, agentName, agentID, event):
        # Remove previous highlighting
        # logging.debug("Handling click on agent in main canvas.")
        self.clearHighlight()
        logging.debug(f"Clicked agentName: {agentName}, agentID: {agentID}")

        # Find iid for specified agent in the treeview
        agentIID = self.parent.parent.simDataView.agentTreeView.tag_has(agentName)

        # Set the selection to include the agent
        self.parent.parent.simDataView.agentTreeView.selection_set(agentIID)
        logging.debug("Agent treeView updated to reflect user selection.")
        
        # Highlight the agent
        agentRef = self.parent.parent.parent.simulationProcess.simAgentManager.agentList.get(agentID)
        agentRef.highlightAgent(multi=False)
        
        # Update the selection tracker
        self.parent.parent.parent.simulationProcess.simAgentManager.currentAgent = agentRef

    def renderAgents(self, graphData, tileSize):
        # Renders agent positions and orientations
        # Render the agent position direct from the graph object
        for node in graphData.nodes(data=True):
            if 'agent' in graphData.nodes.data()[node[0]]:
                # Extract the reference to the agent object with a shallow copy
                agentRef = graphData.nodes.data()[node[0]]['agent']
                logging.debug(f"Node '{node[0]}' contains agent '{agentRef.ID}'.")
                # Extract position data, convert to canvas coordinates and centralize
                nodePosX = agentRef.position[0]
                centerPosX = nodePosX * tileSize + 0.5 * tileSize
                nodePosY = agentRef.position[1]
                centerPosY = nodePosY * tileSize + 0.5 * tileSize
                # Extract the agent orientation
                agentOrientation = agentRef.orientation
                # Tag the agent for layer sorting
                tag = ["agent" + str(agentRef.ID), "agent"]
                # Dictionary of points for the polygon
                dirDict = {
                    "N": (centerPosX, centerPosY - 0.4 * tileSize),
                    "W": (centerPosX - 0.4 * tileSize, centerPosY),
                    "S": (centerPosX, centerPosY + 0.4 * tileSize),
                    "E": (centerPosX + 0.4 * tileSize, centerPosY)
                }
                # Draw the polygon representing the agent
                self.create_polygon(
                    dirDict["N"][0],
                    dirDict["N"][1],
                    dirDict["W"][0],
                    dirDict["W"][1],
                    dirDict["S"][0],
                    dirDict["S"][1],
                    dirDict["E"][0],
                    dirDict["E"][1],
                    outline='black',
                    width = 2,
                    fill='orange',
                    tags=tag
                )
                logging.debug("Agent representation rendered.")

                # Arrow tags should include a sorting tag
                tag.append("agentOrientation")

                # Draw the orientation arrow
                self.create_line(
                    dirDict[agentOrientation][0],
                    dirDict[agentOrientation][1],
                    centerPosX,
                    centerPosY,
                    arrow = tk.FIRST,
                    tags=tag,
                    fill='white',
                    width=4
                )
                logging.debug("Agent orientation rendered.")
            else:
                # print(f"{node} does not contain an agent")
                pass
        logging.info("Rendered all agents in agentManager.")

    def generateHoverInfo(self, graphData, tileSize):
        # Use an object in the canvas to capture the mouse cursor, it will need to be updated with the information relevant to the tile
        # Place one in each cell of the grid that contains a node
        for node in graphData.nodes.data():
            logging.debug(f"Generating hover info for node '{node}'.")
            # Break down the data
            nodeData = node[1]
            nodePosX = nodeData["pos"]["X"]
            nodePosY = nodeData["pos"]["Y"]
            nodeType = nodeData["type"]
            # Create the transparent object
            # Use PIL workaround to create a transparent image, tk.Canvas does not support alpha channels (????)
            tileImage = Image.new('RGBA', (tileSize, tileSize), (255, 255, 255, 0))
            tileImage = ImageTk.PhotoImage(tileImage)
            tileObject = self.create_image(
                nodePosX * tileSize,
                nodePosY * tileSize,
                image=tileImage,
                anchor=tk.NW,
                tags=["infoTile"]
            )
            logging.debug("Mouse capture tile generated.")
            # If there is an agent in the node, include it in the hoverinfo text
            if 'agent' in nodeData:
                nodeAgentName = nodeData['agent'].ID
                nodeAgentID = nodeData['agent'].numID
                hoverString = f"{str(node[0])}: {nodeType.capitalize()}, Agent Name: {nodeAgentName}"
                logging.debug("Node contains an agent, ID added to hover info.")

                # Further, make clicks on this hovertile select the agent
                self.tag_bind(tileObject, "<Button-1>", partial(self.agentClickHighlighter, nodeAgentName, nodeAgentID))
                logging.debug("Bound clicks on the capture tile to the agent.")
            else:
                hoverString = f"{str(node[0])}: {nodeType.capitalize()}"

            # Assign the mouseover event to it
            # Tkinter automatically passes the event object to the handler
            self.tag_bind(tileObject, "<Leave>", partial(self.infoHoverEnter, ". . ."))
            self.tag_bind(tileObject, "<Enter>", partial(self.infoHoverEnter, hoverString))
            logging.debug("Mouseover events bound.")
        logging.info("Generated all information hover tiles.")

    def infoHoverEnter(self, hoverString, event):
        self.infoBoxFrame = self.parent.parent.simInfoBox.simInfoBoxFrame
        self.infoBoxFrame.hoverInfoText.set(hoverString)

    def clearMainCanvas(self):
        # Destroys all entities on the canvas
        self.delete("all")
        logging.info("Main simulation canvas cleared.")

    def sortCanvasLayers(self):
        # Moves all layers to a default order
        # Search for all objects with a specific tag, pull them to the top in the correct order

        # Node objects
        objs = self.find_withtag("node")
        for obj in objs:
            self.lift(obj)
        # Agent objects
        objs = self.find_withtag("agent")
        for obj in objs:
            self.lift(obj)
        # Agent orientation indicator objects
        objs = self.find_withtag("agentOrientation")
        for obj in objs:
            self.lift(obj)
        # Invisible infoTile layer objects
        objs = self.find_withtag("infoTile")
        for obj in objs:
            self.lift(obj)
        logging.info("Canvas object layers sorted.")

    def setAllLayersVisible(self):
        # Mark layer states
        self.danglingEdgeVisibility = True
        self.edgeVisibility = True
        self.nodeVisibility = True
        self.agentVisibility = True
        self.agentOrientationVisibility = True

        # Update the checkboxes
        self.infoBoxButtons = self.parent.parent.simInfoBox.simInfoBoxFrame
        self.infoBoxButtons.danglingEdgeTick.select()
        self.infoBoxButtons.edgeTick.select()
        self.infoBoxButtons.nodeTick.select()
        self.infoBoxButtons.agentTick.select()
        self.infoBoxButtons.agentOrientationTick.select()
        logging.info("All layers set to be visible on the main canvas.")

    def checkLayerVisibility(self):
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

    def toggleLayerVisibility(self, layerTag, state):
        # Find all the objects with the matching tag
        objs = self.find_withtag(layerTag)
        # Toggle their state and visibility
        if state == True:
            state = False
            for obj in objs:
                self.itemconfigure(obj, state='hidden')
        else:
            state = True
            for obj in objs:
                self.itemconfigure(obj, state='normal')
        logging.debug(f"Layer '{layerTag}' toggled from '{state}' to '{not state}'.")
        return state

    def toggleDanglingEdgeVisibility(self):
        self.danglingEdgeVisibility = self.toggleLayerVisibility("danglingEdge", self.danglingEdgeVisibility)

    def toggleEdgeVisibility(self):
        self.edgeVisibility = self.toggleLayerVisibility("edge", self.edgeVisibility)

    def toggleNodeVisibility(self):
        self.nodeVisibility = self.toggleLayerVisibility("node", self.nodeVisibility)

    def toggleAgentVisibility(self):
        self.agentVisibility = self.toggleLayerVisibility("agent", self.agentVisibility)

    def toggleAgentOrientationVisibility(self):
        self.agentOrientationVisibility = self.toggleLayerVisibility("agentOrientation", self.agentOrientationVisibility)

    def highlightTile(self, tileIDX, tileIDY, color, multi, highlightType):
        # Clear the old highlights before drawing this singular highlight
        if multi == False:
            self.clearHighlight(highlightType)
            
        # Draw a translucent highlight over the indicated cell for user guidance
        # tileSize = self.appearanceValues.canvasTileSize
        if isinstance(tileIDX, str):
            tileSize = self.appearanceValues.canvasTileSize
            self.create_rect(
                eval(tileIDX) * tileSize,
                eval(tileIDY) * tileSize,
                eval(tileIDX) * tileSize + tileSize,
                eval(tileIDY) * tileSize + tileSize,
                anchor=tk.NW,
                fill=color,
                alpha=0.3,
                tags=["highlight", highlightType]
            )
        else:
            tileSize = self.appearanceValues.canvasTileSize
            self.create_rect(
                tileIDX * tileSize,
                tileIDY * tileSize,
                tileIDX * tileSize + tileSize,
                tileIDY * tileSize + tileSize,
                anchor=tk.NW,
                fill=color,
                alpha=0.3,
                tags=["highlight", highlightType]
            )
        logging.debug(f"Highlighted tile: ({str(tileIDX)}, {str(tileIDY)})")
        logging.debug(f"With: {color}, multi={multi}, and type {highlightType}")

        # Re-sort the layers so the infolayer is not hidden by the highlight
        self.sortCanvasLayers()

    def clearHighlight(self, highlightType=None):
        # Unsafe function, doesn't check that the kind of removal requested actually exists, fails silently too
        # Remove all objects tagged "highlight" if a type isn't specified
        if highlightType == None:
            self.images = {}
            objs = self.find_withtag("highlight")
            for obj in objs:
                self.delete(obj)
            logging.debug(f"Cleared all highlights.")

    def create_rect(self, x1, y1, x2, y2, **kwargs):
        # https://stackoverflow.com/questions/54637795/how-to-make-a-tkinter-canvas-rectangle-transparent
        # Modified for passing 'anchor' and 'tags' as kwargs
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            anchor = kwargs.pop('anchor')
            tags = kwargs.pop('tags')
            fill = self.parent.parent.winfo_rgb(fill) + (alpha,)
            image = Image.new('RGBA', (x2-x1, y2-y1), fill)
            tkImage = ImageTk.PhotoImage(image)
            self.images[tkImage] = tags
            self.create_image(x1, y1, image=tkImage, anchor=anchor, tags=tags)