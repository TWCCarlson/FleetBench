import tkinter as tk
import math
import pprint
from functools import partial
from PIL import Image, ImageDraw, ImageTk
pp = pprint.PrettyPrinter(indent=4)
import networkx as nx
import logging

class mainView(tk.Frame):
    """
        The primary view of the warehouse, drawn with tk.Canvas layers and organized into a reliable stack
    """
    def __init__(self, parent):
        logging.debug("Main View Canvas UI initializing . . .")
        self.parent = parent

        # Map data reference
        self.mapData = self.parent.mapData.mapGraph
        logging.debug("Map data reference built.")

        # Fetch styling
        self.appearanceValues = self.parent.appearance
        frameHeight = self.appearanceValues.mainViewHeight
        frameWidth = self.appearanceValues.mainViewWidth
        frameBorderWidth = self.appearanceValues.frameBorderWidth
        frameRelief = self.appearanceValues.frameRelief
        logging.debug("Style information retrieved.")

        # Declare frame
        tk.Frame.__init__(self, parent, 
            height=frameHeight, 
            width=frameWidth, 
            borderwidth=frameBorderWidth, 
            relief=frameRelief)
        logging.debug("Containing frame settings constructed.")

        # Render frame within the app window context
        self.grid_propagate(False)
        self.grid(row=1, column=1, sticky=tk.N)
        logging.debug("Containing frame rendered.")
        
        # Build the canvas containing the display information
        logging.debug("Building the canvas . . .")
        self.mainCanvas = mainCanvas(self, self.appearanceValues)

        # Initialize scrolling behavior
        self.initScrolling()
        logging.debug("Main Canvas UI element finished building.")

    def buildReferences(self):
        # Build references to classes declared after this one
        self.contextView = self.parent.contextView
        self.agentManager = self.parent.agentManager
        logging.debug("References built.")

    def initScrolling(self):
        # Create scrollbar components
        self.ybar = tk.Scrollbar(self, orient="vertical")
        self.xbar = tk.Scrollbar(self, orient="horizontal")
        logging.debug("Scrollbar component classes built.")

        # Bind the scrollbars to the canvas
        self.ybar["command"] = self.mainCanvas.yview
        self.xbar["command"] = self.mainCanvas.xview
        logging.debug("Bound scrollbars to canvas viewspace.")

        # Adjust positioning, size relative to grid
        self.ybar.grid(column=1, row=0, sticky="ns")
        self.xbar.grid(column=0, row=1, sticky="ew")
        logging.debug("Rendered canvas scrollbars.")

        # Make canvas update scrollbar position to match its view
        self.mainCanvas["yscrollcommand"] = self.ybar.set
        self.mainCanvas["xscrollcommand"] = self.xbar.set
        logging.debug("Main canvas scroll commands bound to scrollbars.")

        # Bind mousewheel to interact with the scrollbars
        # Only do this when the cursor is inside this frame
        self.bind('<Enter>', self.bindMousewheel)
        self.bind('<Leave>', self.unbindMousewheel)
        logging.debug("Mouse input capture bounds established for Main Canvas.")

        # Reset the view
        self.mainCanvas.xview_moveto("0.0")
        self.mainCanvas.yview_moveto("0.0")
        logging.debug("Scrollbar, Canvas position default set.")

    def bindMousewheel(self, event):
        self.bind_all("<MouseWheel>", self.mousewheelAction)
        self.bind_all("<Shift-MouseWheel>", self.shiftMousewheelAction)
        logging.debug("Bound mousewheel inputs to scrollbar.")

    def unbindMousewheel(self, event):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Shift-MouseWheel>")
        logging.debug("Released mousewheel input bindings due to cursor leaving the canvas.")

    def mousewheelAction(self, event):
        self.mainCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def shiftMousewheelAction(self, event):
        self.mainCanvas.xview_scroll(int(-1*(event.delta/120)), "units")

class mainCanvas(tk.Canvas):
    """
        The primary view of the warehouse, drawn with tk.Canvas layers and organized into a reliable stack
        Probably needs organizational refactor
    """
    def __init__(self, parent, appearanceValues):
        logging.info("Initializing the main canvas class . . .")

        tk.Canvas.__init__(self, parent)
        self.parent = parent
        self.appearanceValues = appearanceValues
        self["bg"] = self.appearanceValues.canvasBackgroundColor
        self["width"] = self.appearanceValues.canvasDefaultWidth
        self["height"] = self.appearanceValues.canvasDefaultHeight
        self["scrollregion"] = (0,0,self["width"], self["height"])
        self.canvasTileSize = self.appearanceValues.canvasTileSize
        logging.info("Main Canvas UI element style settings built.")

        # Render canvas within the mainView frame context
        # Give it size priority to fill the whole frame
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.grid(column=0, row=0, sticky=tk.N+tk.S+tk.E+tk.W)
        logging.info("Rendered Main Canvas in main app.")

        # Container for highlighted tiles
        self.images = {}

        # Draw gridlines
        self.drawGridlines()

    def drawGridlines(self):
        # Draw them at each tile width
        # self.create_rectangle(0, 0, self["height"], self["width"], fill="red")
        # +1 for the extra line, +1 for making range inclusive
        # Horizontal Lines
        logging.debug("Rendering Main Canvas gridlines . . .")
        for i in range(math.floor(int(self["height"])/self.canvasTileSize)+1):
            self.create_line(0, i*self.canvasTileSize, self["width"], i*self.canvasTileSize, fill=self.appearanceValues.canvasGridlineColor)
        # Vertical lines
        for i in range(math.floor(int(self["width"])/self.canvasTileSize)+1):
            self.create_line(i*self.canvasTileSize, 0, i*self.canvasTileSize, self["height"], fill=self.appearanceValues.canvasGridlineColor)

    def graphCoordToCanvas(self, coord):
        tileSize = self.appearanceValues.canvasTileSize
        # In: the tile count value for location of the coord
        # Out: the canvas pixel value for location of the coord
        canvasCoord = coord * tileSize + 0.5 * tileSize
        logging.debug(f"Converted tile coordinate '{coord}' to canvas coordinate '{canvasCoord}'")
        return canvasCoord

    def renderGraphState(self):
        logging.info("Re-rendering all graph state data.")
        graphData = self.parent.mapData
        # Input: NetworkX graph
        # Output: render the tiles of the map, including
        #   - Node tiles
        #   - Edges
        #   - Colorization by type
        #   - Agents
        #   - Context tiles
        # Style references
        tileSize = self.appearanceValues.canvasTileSize
        nodeSizeRatio = self.appearanceValues.canvasTileCircleRatio
        edgeWidth = self.appearanceValues.canvasEdgeWidth
        logging.info("Fetched style reference values.")
        # Clear current canvas
        logging.info("Attempting to clear the canvas for re-render . . .") 
        self.clearMainCanvas()
        # Draw tiles, being sure to tag them for ordering and overlaying
        logging.info("Attempting to re-render grid lines . . .")
        self.drawGridlines()
        logging.info("Attempting to re-render graph data nodes . . .")
        self.renderNodes(graphData, tileSize, nodeSizeRatio)
        logging.info("Attempting to re-render graph data edges . . .")
        self.renderEdges(graphData, edgeWidth)
        logging.info("Attempting to re-render unconnected graph data edges . . .")
        self.renderDanglingEdges(graphData, tileSize, edgeWidth)
        logging.info("Attempting to re-render agentManager agents . . .")
        self.renderAgents(graphData, tileSize)
        logging.info("Attempting to build hover info . . .")
        self.generateHoverInfo(graphData, tileSize)
        logging.info("Sorting re-rendered layers for visibility . . .")
        self.sortCanvasLayers()
        logging.info("Managing layer visibility according to infoBox settings . . .")
        self.checkLayerVisibility()
        logging.info("Canvas re-render finished.")
        
    def renderNodes(self, graphData, tileSize, nodeSizeRatio):
        # Display nodes in graph
        for node in graphData.nodes.data():
            logging.debug(f"Attempting to draw node: {node}")
            # Break down the data
            nodeData = node[1]
            nodePosX = nodeData["pos"]["X"]
            nodePosY = nodeData["pos"]["Y"]
            nodeType = nodeData["type"]

            # Identify the center of the canvas tile
            logging.debug("Identifying canvas coordinate of node:")
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
                logging.debug(f"Node is of type 'void', ignoring . . .")
                continue
            logging.debug(f"Node type '{nodeType}' is assigned tags: {tags}")

            # Draw the node
            self.create_oval(
                nodePosGraphX - nodeSizeRatio * tileSize,
                nodePosGraphY - nodeSizeRatio * tileSize,
                nodePosGraphX + nodeSizeRatio * tileSize,
                nodePosGraphY + nodeSizeRatio * tileSize,
                fill = fillColor,
                tags=tags
            )
            logging.debug("Node drawn successfully.")
        logging.info("Rendered all graphData nodes.")

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
        # Display dangling edges
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

    def agentClickHighlighter(self, agentName, agentID, event):
        # Remove previous highlighting
        logging.debug("Handling click on agent in main canvas.")
        self.clearHighlight()
        logging.debug(f"Clicked agentName: {agentName}, agentID: {agentID}")

        # Find iid for specified agent in the treeview
        agentIID = self.parent.contextView.agentTreeView.tag_has(agentName)

        # Set the selection to include the agent
        # self.parent.contextView.objectTreeView.see(agentIID)
        self.parent.contextView.agentTreeView.selection_set(agentIID)
        logging.debug("Agent treeView updated to reflect user selection.")

        # Highlight the agent
        agentRef = self.parent.agentManager.agentList.get(agentID)
        agentRef.highlightAgent(multi=False)

        # Update the selection tracker
        self.parent.parent.agentManager.currentAgent = agentRef
        
        # Update movement choices for the selected agent
        self.parent.parent.contextView.validateMovementButtonStates()

        # Enable management of the agent state in the toolBar
        self.parent.parent.toolBar.enableAgentManagement()

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
        self.infoBoxFrame = self.parent.parent.infoBox.infoBoxFrame
        self.infoBoxFrame.hoverInfoText.set(hoverString)

    def clearMainCanvas(self):
        self.delete("all")
        logging.info("Main canvas cleared.")

    def sortCanvasLayers(self):
        # Orders the stuff on the canvas to a default order
        # Find all objects with each tag
        # Pull them to the front in the right order
        
        # Node icons
        objs = self.find_withtag("node")
        for obj in objs:
            self.lift(obj)
        # Agent icons
        objs = self.find_withtag("agent")
        for obj in objs:
            self.lift(obj)
        # Agent orientation indicators
        objs = self.find_withtag("agentOrientation")
        for obj in objs:
            self.lift(obj)
        # Invisible infoTile layer
        objs = self.find_withtag("infoTile")
        for obj in objs:
            self.lift(obj)
        logging.info("Canvas object layers sorted.")
        # self.setAllLayersVisible()

    def setAllLayersVisible(self):
        # Mark layer states
        self.danglingEdgeVisibility = True
        self.edgeVisibility = True
        self.nodeVisibility = True
        self.agentVisibility = True
        self.agentOrientationVisibility = True

        # Update the checkboxes
        self.infoBoxButtons = self.parent.parent.infoBox.infoBoxFrame
        self.infoBoxButtons.danglingEdgeTick.select()
        self.infoBoxButtons.edgeTick.select()
        self.infoBoxButtons.nodeTick.select()
        self.infoBoxButtons.agentTick.select()
        self.infoBoxButtons.agentOrientationTick.select()
        logging.info("All layers set to be visible on the main canvas.")

    def checkLayerVisibility(self):
        layerStates = {
            "danglingEdge": self.danglingEdgeVisibility,
            "edge": self.edgeVisibility,
            "node": self.nodeVisibility,
            "agent": self.agentVisibility,
            "agentOrientation": self.agentOrientationVisibility
        }
        for layer in layerStates:
            self.setLayerVisibility(layer, layerStates[layer])
        logging.info("Updated layer visibilities to match user settings.")

    def setLayerVisibility(self, layerTag, desiredState):
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

        # If a type is specified, only delete highlights of that type
        else:
            objs = self.find_withtag(highlightType)
            for obj in objs:
                self.delete(obj)
            for image in list(self.images.keys()):
                if highlightType in self.images[image]:
                    del self.images[image]
            logging.debug(f"Cleared old highlight of type {highlightType}")

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
